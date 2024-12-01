from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/processUrl')
def greet():
    url = request.args.get('url', 'мир')
    print('recibi este URL:' + url)
    return f"URL:, {url}!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to Render's port 10000
    app.run(host='0.0.0.0', port=port)