from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        resp = requests.get(url, timeout=4)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = '\n'.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
