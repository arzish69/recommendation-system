import random

class RecommendationEngine:
    def __init__(self):
        # Sample article database - in a real application, this would come from a real database
        self.articles = {
            'Technology': [
                {'title': 'The Future of AI', 'url': 'https://example.com/ai-future', 'description': 'Exploring the latest developments in artificial intelligence.'},
                {'title': '5G Revolution', 'url': 'https://example.com/5g', 'description': 'How 5G is changing the world of connectivity.'}
            ],
            'Science': [
                {'title': 'Mars Exploration', 'url': 'https://example.com/mars', 'description': 'Latest discoveries from the red planet.'},
                {'title': 'Quantum Computing', 'url': 'https://example.com/quantum', 'description': 'Understanding quantum supremacy.'}
            ],
            # Add more sample articles for other categories...
        }

    def get_recommendations(self, categories, num_recommendations=2):
        recommendations = []
        for category in categories:
            if category in self.articles:
                articles = self.articles.get(category, [])
                recommendations.extend(random.sample(articles, min(num_recommendations, len(articles))))
        return recommendations