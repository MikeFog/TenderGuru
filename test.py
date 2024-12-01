from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/processUrl')
def greet():
    url = request.args.get('url', 'мир')
    # Формируем сложный объект для возврата
    result = {
        "contest_name": "Конкурс №31231",
        "description": f"Надо обработать конкурс по такому адресу:, {url}!"
    }
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to Render's port 10000
    app.run(host='0.0.0.0', port=port)