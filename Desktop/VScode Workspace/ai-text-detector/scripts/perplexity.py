#!/usr/bin/env python3
"""Persistent HTTP server for token-level features (llama.cpp) + DeBERTa classifier.

When models/detector/ exists, also returns 4-class classification
(human / ai / ai_polished / human_polished) alongside token data.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

import numpy as np

LABEL_NAMES = ["human", "ai", "ai_polished", "human_polished"]

# ── DeBERTa classifier (optional) ──────────────────────────────────────────

def load_classifier():
    """Load DeBERTa classifier from models/detector/ if available."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.environ.get(
        "CLASSIFIER_PATH",
        os.path.join(script_dir, "..", "models", "detector"),
    )

    if not os.path.isdir(model_dir):
        print(f"Classifier not found at {model_dir} -- running without it.", file=sys.stderr)
        return None, None

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch

        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        model.float()
        model.eval()
        if torch.cuda.is_available():
            model = model.cuda()
        print(f"Classifier loaded from {model_dir}", file=sys.stderr)
        return tokenizer, model
    except Exception as e:
        print(f"Failed to load classifier: {e}", file=sys.stderr)
        return None, None


def classify_text(tokenizer, model, text):
    """Run DeBERTa 4-class inference, return label + probabilities."""
    import torch

    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    label = int(np.argmax(probs))
    return {
        "label": label,
        "label_name": LABEL_NAMES[label],
        "probabilities": {name: round(float(probs[i]), 4) for i, name in enumerate(LABEL_NAMES)},
        "ai_score": round(float(probs[1] + probs[2]) * 100, 1),
    }


# ── Llama.cpp perplexity model ─────────────────────────────────────────────

def load_model():
    model_path = os.environ.get(
        "MODEL_PATH",
        os.path.expanduser(
            "~/.ollama/models/blobs/sha256-74701a8c35f6c8d9a4b91f3f3497643001d63e0c7a84e085bed452548fa88d45"
        ),
    )

    if not os.path.exists(model_path):
        print(f"Perplexity model not found at: {model_path}", file=sys.stderr)
        print("Token-level analysis disabled. Run: ollama pull llama3.2:1b", file=sys.stderr)
        return None

    try:
        from llama_cpp import Llama

        return Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            logits_all=True,
            verbose=False,
        )
    except Exception as e:
        print(f"Failed to load perplexity model: {e}", file=sys.stderr)
        print("Token-level analysis disabled.", file=sys.stderr)
        return None


def compute_features(model, text):
    token_ids = model.tokenize(text.encode("utf-8"), add_bos=True)
    n_tokens = len(token_ids)

    if n_tokens < 2:
        return {"error": "Text too short for analysis"}

    if n_tokens > 2048:
        token_ids = token_ids[:2048]
        n_tokens = 2048

    # Suppress llama.cpp C-level logs during inference
    stderr_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)

    try:
        model.reset()
        model.eval(token_ids)
    finally:
        os.dup2(stderr_fd, 2)
        os.close(devnull)
        os.close(stderr_fd)

    results = []
    for i in range(1, n_tokens):
        logits = np.array(model.scores[i - 1], dtype=np.float64)
        logits -= np.max(logits)
        probs = np.exp(logits)
        probs /= np.sum(probs)

        actual_id = token_ids[i]
        actual_prob = float(probs[actual_id])
        logprob = float(np.log(max(actual_prob, 1e-20)))

        rank = int(np.sum(probs > actual_prob)) + 1

        valid = probs > 1e-10
        entropy = float(-np.sum(probs[valid] * np.log(probs[valid])))

        token_bytes = model.detokenize([actual_id])
        token_str = token_bytes.decode("utf-8", errors="replace")

        results.append({
            "token": token_str,
            "logprob": logprob,
            "rank": rank,
            "entropy": entropy,
        })

    return {"tokens": results}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        text = body.get("text", "").strip()

        if not text:
            result = {"error": "No text provided"}
        else:
            try:
                if self.server.model:
                    result = compute_features(self.server.model, text)
                else:
                    result = {"tokens": []}
                # Add DeBERTa classification if available
                clf_tok = self.server.classifier_tokenizer
                clf_mod = self.server.classifier_model
                if clf_tok and clf_mod:
                    result["classification"] = classify_text(clf_tok, clf_mod, text)
            except Exception as e:
                result = {"error": str(e)}

        response = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        pass


class PerplexityServer(HTTPServer):
    allow_reuse_address = True

    def __init__(self, addr, handler, model, classifier_tokenizer=None, classifier_model=None):
        super().__init__(addr, handler)
        self.model = model
        self.classifier_tokenizer = classifier_tokenizer
        self.classifier_model = classifier_model


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("Loading perplexity model...", file=sys.stderr)
    model = load_model()
    print("Loading classifier...", file=sys.stderr)
    clf_tokenizer, clf_model = load_classifier()
    print(f"Server running at http://127.0.0.1:{port}", file=sys.stderr)
    server = PerplexityServer(("127.0.0.1", port), Handler, model, clf_tokenizer, clf_model)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", file=sys.stderr)
