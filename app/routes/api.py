from flask import Blueprint, request, jsonify
from app.models.recommender import ArticleRecommender
from app.utils.helpers import validate_request_data
import pickle
import os

api_bp = Blueprint('api', __name__)
recommender = ArticleRecommender()

@api_bp.route('/train', methods=['POST'])
def train_model():
    """Train/update the recommendation model with new data"""
    try:
        data = request.get_json()
        if not validate_request_data(data, ['url_data']):
            return jsonify({'error': 'Invalid request data'}), 400
            
        recommender.preprocess_url_content(data['url_data'])
        
        # Save model state
        save_path = os.path.join(Config.MODEL_SAVE_PATH, 'recommender.pkl')
        with open(save_path, 'wb') as f:
            pickle.dump(recommender, f)
            
        return jsonify({'message': 'Model trained successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/update-user-profile', methods=['POST'])
def update_user_profile():
    """Update a user's profile with new interaction data"""
    try:
        data = request.get_json()
        if not validate_request_data(data, ['user_id', 'interactions']):
            return jsonify({'error': 'Invalid request data'}), 400
            
        recommender.update_user_profile(
            data['user_id'],
            data['interactions']
        )
        
        return jsonify({'message': 'User profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/update-group-profile', methods=['POST'])
def update_group_profile():
    """Update a group's profile"""
    try:
        data = request.get_json()
        if not validate_request_data(data, ['group_id', 'member_ids']):
            return jsonify({'error': 'Invalid request data'}), 400
            
        recommender.update_group_profile(
            data['group_id'],
            data['member_ids']
        )
        
        return jsonify({'message': 'Group profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get recommendations for a user"""
    try:
        user_id = request.args.get('user_id')
        group_ids = request.args.getlist('group_ids')
        n_recommendations = int(request.args.get('n_recommendations', 10))
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
            
        recommendations = recommender.get_recommendations(
            user_id=user_id,
            group_ids=group_ids,
            n_recommendations=n_recommendations
        )
        
        return jsonify({'recommendations': recommendations}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/similar-articles', methods=['GET'])
def get_similar_articles():
    """Get similar articles for a given URL"""
    try:
        url = request.args.get('url')
        n_similar = int(request.args.get('n_similar', 5))
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
            
        similar_articles = recommender.get_similar_articles(
            url=url,
            n_similar=n_similar
        )
        
        return jsonify({'similar_articles': similar_articles}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500