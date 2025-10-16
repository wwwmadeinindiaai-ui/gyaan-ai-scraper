from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Get URL from JSON payload
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required in JSON payload'}), 400
        
        url = data['url']
        
        # Fetch the webpage
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all paragraphs and headings
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings.extend([h.get_text(strip=True) for h in soup.find_all(tag)])
        
        return jsonify({
            'url': url,
            'headings': headings,
            'paragraphs': paragraphs,
            'status': 'success'
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'gyaan-ai-scraper'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
