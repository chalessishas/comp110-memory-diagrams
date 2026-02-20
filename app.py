from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

# 配置 Claude
import os
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)