import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from datetime import datetime, timedelta

class ArticleRecommender:
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.url_to_idx = {}
        self.idx_to_url = {}
        self.user_profiles = defaultdict(lambda: defaultdict(float))
        self.group_profiles = defaultdict(lambda: defaultdict(float))
        
    def preprocess_url_content(self, url_data):
        """
        Process URL content into features for recommendation
        
        Args:
            url_data: List of dictionaries containing:
                - url: string
                - title: string
                - content: string (from reader view)
                - highlights: list of highlighted text
                - notes: list of sticky notes
                - tags: list of tags (if any)
        """
        documents = []
        for idx, item in enumerate(url_data):
            self.url_to_idx[item['url']] = idx
            self.idx_to_url[idx] = item['url']
            
            # Combine all relevant text
            text = f"{item['title']} {item['content']}"
            if item.get('highlights'):
                text += f" {' '.join(item['highlights'])}"
            if item.get('notes'):
                text += f" {' '.join(item['notes'])}"
            if item.get('tags'):
                text += f" {' '.join(item['tags'])}"
            
            documents.append(text)
            
        self.content_matrix = self.tfidf.fit_transform(documents)
        self.similarity_matrix = cosine_similarity(self.content_matrix)
        
    def update_user_profile(self, user_id, interaction_data, decay_factor=0.1):
        """
        Update user profile based on their interactions
        
        Args:
            user_id: string
            interaction_data: List of dictionaries containing:
                - url: string
                - interaction_type: string (view/bookmark/highlight/note)
                - timestamp: datetime
                - time_spent: float (minutes)
        """
        for interaction in interaction_data:
            url_idx = self.url_to_idx[interaction['url']]
            
            # Calculate interaction weight
            weight = self._calculate_interaction_weight(interaction)
            
            # Apply time decay
            days_old = (datetime.now() - interaction['timestamp']).days
            time_decay = np.exp(-decay_factor * days_old)
            
            # Update user profile
            self.user_profiles[user_id][url_idx] += weight * time_decay
            
    def _calculate_interaction_weight(self, interaction):
        """Calculate weight based on interaction type and engagement"""
        base_weights = {
            'view': 1.0,
            'bookmark': 2.0,
            'highlight': 3.0,
            'note': 4.0
        }
        
        weight = base_weights[interaction['interaction_type']]
        
        # Adjust weight based on time spent
        if interaction.get('time_spent'):
            weight *= min(1 + (interaction['time_spent'] / 10.0), 3.0)
            
        return weight
        
    def update_group_profile(self, group_id, member_ids):
        """Update group profile based on member profiles"""
        group_vector = np.zeros(len(self.url_to_idx))
        
        for user_id in member_ids:
            if user_id in self.user_profiles:
                for url_idx, weight in self.user_profiles[user_id].items():
                    group_vector[url_idx] += weight
                    
        # Normalize group vector
        if np.sum(group_vector) > 0:
            group_vector = group_vector / np.sum(group_vector)
            
        self.group_profiles[group_id] = group_vector
        
    def get_recommendations(self, user_id, group_ids=None, n_recommendations=10):
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: string
            group_ids: list of group IDs the user belongs to
            n_recommendations: number of recommendations to return
            
        Returns:
            List of recommended URLs with scores
        """
        # Initialize recommendation scores
        scores = np.zeros(len(self.url_to_idx))
        
        # Content-based recommendations
        if user_id in self.user_profiles:
            for url_idx, weight in self.user_profiles[user_id].items():
                scores += weight * self.similarity_matrix[url_idx]
                
        # Group-based recommendations
        if group_ids:
            group_weight = 0.3  # Adjust influence of group preferences
            for group_id in group_ids:
                if group_id in self.group_profiles:
                    scores += group_weight * self.group_profiles[group_id]
                    
        # Filter out already interacted items
        interacted_urls = set(self.user_profiles[user_id].keys())
        scores[list(interacted_urls)] = -np.inf
        
        # Get top recommendations
        top_indices = np.argsort(scores)[-n_recommendations:][::-1]
        recommendations = [
            {
                'url': self.idx_to_url[idx],
                'score': float(scores[idx])
            }
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return recommendations

    def get_similar_articles(self, url, n_similar=5):
        """Get similar articles based on content similarity"""
        if url not in self.url_to_idx:
            return []
            
        url_idx = self.url_to_idx[url]
        similarities = self.similarity_matrix[url_idx]
        
        # Get top similar articles
        similar_indices = np.argsort(similarities)[-n_similar-1:][::-1]
        similar_articles = [
            {
                'url': self.idx_to_url[idx],
                'similarity': float(similarities[idx])
            }
            for idx in similar_indices
            if idx != url_idx
        ]
        
        return similar_articles