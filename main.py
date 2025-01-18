from flask import Flask, render_template, request, jsonify
from app.models.recommender import WebNewsEngine
from app.config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the web news engine
news_engine = WebNewsEngine()

@app.route('/')
def index():
    return render_template('index.html', config=app.config)

@app.route('/check_scraping_status')
def check_scraping_status():
    status = news_engine.get_scraping_status()
    return jsonify(status)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    selected_categories = request.json.get('categories', [])
    if len(selected_categories) != 3:
        return jsonify({'error': 'Please select exactly 3 categories'}), 400
    
    recommendations = news_engine.get_recommendations(selected_categories)
    
    # Group recommendations by category
    grouped_recommendations = {
        'individual': [],
        'combined': []
    }
    
    for rec in recommendations:
        if '&' in rec['category']:
            grouped_recommendations['combined'].append(rec)
        else:
            grouped_recommendations['individual'].append(rec)
    
    return jsonify(grouped_recommendations)

if __name__ == '__main__':
    app.run(debug=True)