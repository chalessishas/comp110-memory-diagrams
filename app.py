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
    
    # 构造 Prompt
    prompt = f"请将以下内容翻译成英文，只输出结果：{text}"
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return jsonify({"result": response.content[0].text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)