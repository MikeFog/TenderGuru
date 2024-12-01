from flask import Flask, request

app = Flask(__name__)

@app.route('/processUrl')
def greet():
    url = request.args.get('url', 'мир')
    print('recibi este URL:' + url)
    return f"URL:, {url}!"

if __name__ == '__main__':
    app.run(debug=True)