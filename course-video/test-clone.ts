const DASHSCOPE_CUSTOM_ENDPOINT =
  "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization";

async function main() {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) throw new Error("DASHSCOPE_API_KEY not set");

  // Step 1: Register voice
  console.log("Registering voice clone...");
  const res = await fetch(DASHSCOPE_CUSTOM_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "voice-enrollment",
      input: {
        action: "create_voice",
        target_model: "cosyvoice-v3-plus",
        prefix: "coursevc",
        url: "https://files.catbox.moe/d6lvzq.wav",
        language_hints: ["zh"],
        max_prompt_audio_length: 30.0,
      },
    }),
  });

  const data = await res.json();
  console.log("Response:", JSON.stringify(data, null, 2));

  if (data.output?.voice_id) {
    console.log("Voice ID:", data.output.voice_id);
    // Save voice_id for future use
    const { writeFileSync } = await import("fs");
    writeFileSync("./voice/voice-id.txt", data.output.voice_id);
  }
}

main().catch(console.error);
