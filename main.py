from flask import Flask, render_template, request, jsonify
from app.models.recommender import RecommendationEngine
from app.config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the recommendation engine
recommender = RecommendationEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_api_limits')
def check_api_limits():
    limits = recommender.check_api_limits()
    return jsonify(limits)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    selected_categories = request.json.get('categories', [])
    if len(selected_categories) != 3:
        return jsonify({'error': 'Please select exactly 3 categories'}), 400
    
    recommendations = recommender.get_recommendations(selected_categories)
    
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