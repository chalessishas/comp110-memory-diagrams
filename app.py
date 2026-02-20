from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    targetLang = data.get('targetLang', '英文')
    # 构造 Prompt
    prompt = f"请自动识别以下文字的语言，然后翻译成{targetLang}，只输出翻译结果：{text}"
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return jsonify({"result": response.content[0].text})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_file = request.files['audio']
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=(audio_file.filename, audio_file.read(), audio_file.mimetype)
    )
    return jsonify({"result": transcript.text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)