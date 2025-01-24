# recommender.py
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np

class BasicRecommender:
    def __init__(self):
        # Initialize Firebase (you'll need to add your credentials)
        if not firebase_admin._apps:
            cred = credentials.Certificate('service_acc.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    async def get_user_links(self, user_id: str) -> List[Dict]:
        """Get user's saved links"""
        links = []
        links_ref = self.db.collection('users').document(user_id).collection('links')
        
        # Convert to async operation
        docs = links_ref.order_by('timestamp', direction='DESCENDING').limit(50).stream()
        
        for doc in docs:
            data = doc.to_dict()
            links.append({
                'id': doc.id,
                'url': data.get('url'),
                'title': data.get('title', ''),  # Provide default empty string
                'timestamp': data.get('timestamp')
            })
        
        return links
    
    async def get_other_users_links(self, current_user_id: str) -> List[Dict]:
        """Get links from other users (limited sample for recommendations)"""
        all_links = []
        users_ref = self.db.collection('users')
        
        # Convert to async operation
        user_docs = users_ref.limit(10).stream()
        
        for user_doc in user_docs:
            if user_doc.id == current_user_id:
                continue
                
            links_ref = users_ref.document(user_doc.id).collection('links')
            link_docs = links_ref.order_by('timestamp', direction='DESCENDING').limit(20).stream()
            
            for doc in link_docs:
                data = doc.to_dict()
                all_links.append({
                    'id': doc.id,
                    'url': data.get('url'),
                    'title': data.get('title', ''),  # Provide default empty string
                    'timestamp': data.get('timestamp')
                })
        
        return all_links
    
    def get_recommendations(self, user_links: List[Dict], candidate_links: List[Dict], n_recommendations: int = 5) -> List[Dict]:
        # Filter links with non-empty titles
        user_links = [link for link in user_links if link.get('title') and link['title'].strip()]
        candidate_links = [link for link in candidate_links if link.get('title') and link['title'].strip()]

        if not user_links or not candidate_links:
            return []
        
        # Extract titles
        user_titles = [link['title'] for link in user_links]
        candidate_titles = [link['title'] for link in candidate_links]
        
        try:
            # Combine titles for TF-IDF
            all_titles = user_titles + candidate_titles
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(all_titles)
            
            # Calculate average user profile
            user_profile = np.asarray(tfidf_matrix[:len(user_titles)].mean(axis=0)).flatten()
            
            # Calculate similarities
            candidate_matrix = tfidf_matrix[len(user_titles):]
            candidate_similarities = cosine_similarity(
                user_profile.reshape(1, -1),
                candidate_matrix
            )[0]
            
            # Get top recommendations
            top_indices = candidate_similarities.argsort()[-n_recommendations:][::-1]
            recommendations = [candidate_links[i] for i in top_indices]
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []