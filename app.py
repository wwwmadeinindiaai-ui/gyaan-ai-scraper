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

@app.route('/search', methods=['POST'])
def internet_search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Missing "query" parameter'}), 400
    url = f'https://api.duckduckgo.com/?q={query}&format=json'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        # Parse DuckDuckGo results top-level RelatedTopics array
        parsed = []
        for topic in results.get('RelatedTopics', []):
            if isinstance(topic, dict):
                entry = {
                    'text': topic.get('Text'),
                    'url': topic.get('FirstURL')
                }
                parsed.append(entry)
            elif 'Topics' in topic:
                for subtopic in topic['Topics']:
                    entry = {
                        'text': subtopic.get('Text'),
                        'url': subtopic.get('FirstURL')
                    }
                    parsed.append(entry)
        return jsonify({
            'query': query,
            'results': parsed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/google_search', methods=['POST'])
def google_search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Missing "query" parameter'}), 400
google_api_key = os.environ.get('GOOGLE_API_KEY')
google_cse_id = os.environ.get('GOOGLE_CSE_ID')

    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': google_api_key,
        'cx': google_cse_id,
        'q': query,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        parsed = []
        for item in results.get('items', []):
            entry = {
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'link': item.get('link')
            }
            parsed.append(entry)
        return jsonify({
            'query': query,
            'results': parsed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_gemini():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Missing "prompt" parameter'}), 400
    import os
gemini_api_key = os.environ.get('GEMINI_API_KEY')


    url = 'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent'
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': gemini_api_key
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        results = resp.json()
        replies = []
        for candidate in results.get('candidates', []):
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'text' in part:
                        replies.append(part['text'])
        return jsonify({'prompt': prompt, 'responses': replies})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'gyaan-ai-scraper'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
