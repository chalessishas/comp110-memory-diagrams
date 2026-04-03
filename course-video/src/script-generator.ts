import Anthropic from "@anthropic-ai/sdk";
import { readFileSync } from "fs";
import { CourseScript, CourseScriptSchema } from "./types.js";

const SYSTEM_PROMPT = `You are an expert educational content designer. Your job is to create structured teaching scripts for blackboard-style lecture videos.

Given a topic (and optionally reference material), output a CourseScript JSON with:
- A clear title
- 5-12 segments, each with narration text and board actions
- Natural teaching progression: hook → concept → example → formula → summary

Rules for board actions:
- write_text: Use for definitions, key terms, examples. Give meaningful IDs.
- show_formula: Use LaTeX syntax. Give IDs so arrows/highlights can reference them.
- draw_arrow: Reference IDs of previously written elements.
- highlight: Reference IDs of previously written elements. Use "yellow" or "red".
- erase: Use target "all" when transitioning to a major new topic (like flipping to a clean board).
- pause: Use for dramatic effect or to let concepts sink in (0.5-2 seconds).

Keep narration conversational and clear. Each segment should be 15-45 seconds when spoken.
Write board content concisely — this is a blackboard, not a textbook page.
Always give IDs to elements that will be referenced later by arrows or highlights.

IMPORTANT: Write ALL narration text in Chinese (中文). Board text (write_text) should also be in Chinese.
Formulas (show_formula) use standard LaTeX notation.

Output ONLY valid JSON matching the CourseScript schema. No markdown, no explanation.`;

const EXAMPLE_SCRIPT: CourseScript = {
  title: "Quadratic Formula",
  segments: [
    {
      narration:
        "Let's start with something you've seen before — a quadratic equation.",
      board: [
        {
          type: "write_text",
          id: "quad-eq",
          text: "Quadratic Equation",
        },
        {
          type: "show_formula",
          id: "general-form",
          latex: "ax^2 + bx + c = 0",
        },
      ],
    },
    {
      narration:
        "The quadratic formula gives us the solutions directly. Here it is.",
      board: [
        {
          type: "show_formula",
          id: "qf",
          latex: "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
        },
        { type: "pause", duration: 1.5 },
        {
          type: "draw_arrow",
          from: "general-form",
          to: "qf",
        },
      ],
    },
    {
      narration:
        "The key part is what's under the square root — the discriminant. It tells us how many solutions we have.",
      board: [
        {
          type: "highlight",
          target: "qf",
          color: "yellow",
        },
        {
          type: "write_text",
          id: "disc-label",
          text: "Discriminant: b² - 4ac",
        },
      ],
    },
  ],
};

interface GenerateOptions {
  topic: string;
  sourceFile?: string;
  model?: string;
}

export async function generateScript(
  options: GenerateOptions
): Promise<CourseScript> {
  const { topic, sourceFile, model } = options;

  let userMessage = `Create a teaching script for the topic: "${topic}"`;
  if (sourceFile) {
    const content = readFileSync(sourceFile, "utf-8");
    userMessage += `\n\nReference material:\n${content.slice(0, 15000)}`;
  }

  userMessage += `\n\nHere is an example of the expected output format:\n${JSON.stringify(EXAMPLE_SCRIPT, null, 2)}`;

  // DeepSeek via OpenAI-compatible API
  if (model === "deepseek") {
    return generateWithDeepSeek(userMessage);
  }

  // Default: Claude
  const client = new Anthropic();
  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 8192,
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content: userMessage }],
  });

  const text =
    response.content[0].type === "text" ? response.content[0].text : "";
  return parseAndValidate(text);
}

async function generateWithDeepSeek(userMessage: string): Promise<CourseScript> {
  const apiKey = process.env.DEEPSEEK_API_KEY;
  if (!apiKey) throw new Error("DEEPSEEK_API_KEY not set");

  const res = await fetch("https://api.deepseek.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "deepseek-chat",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userMessage },
      ],
      max_tokens: 8192,
      response_format: { type: "json_object" },
    }),
  });

  if (!res.ok) {
    throw new Error(`DeepSeek API error: ${res.status} ${await res.text()}`);
  }

  const data = (await res.json()) as {
    choices: { message: { content: string } }[];
  };
  return parseAndValidate(data.choices[0].message.content);
}

function parseAndValidate(raw: string): CourseScript {
  // Strip markdown code fences if present
  const cleaned = raw.replace(/^```(?:json)?\n?/m, "").replace(/\n?```$/m, "");
  const parsed = JSON.parse(cleaned);
  return CourseScriptSchema.parse(parsed);
}
