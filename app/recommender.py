from .feed_parser import FeedParser
from urllib.parse import urlparse
import asyncio
from collections import Counter
import re

class TopicBasedRecommender:
    def __init__(self):
        self.feed_parser = FeedParser()
        
    def calculate_topic_score(self, text, interests):
        text = text.lower()
        # Topic keywords for each interest
        topic_keywords = {
            'Technology': ['tech', 'software', 'digital', 'ai', 'computer', 'app', 'cyber'],
            'Science': ['research', 'study', 'scientist', 'discovery', 'lab', 'physics'],
            'Business': ['market', 'company', 'startup', 'finance', 'industry', 'trade'],
            'Arts': ['artist', 'exhibition', 'museum', 'gallery', 'painting', 'sculpture'],
            'Politics': ['government', 'policy', 'election', 'congress', 'political', 'vote'],
            'Food': ['recipe', 'restaurant', 'cuisine', 'cooking', 'chef', 'meal'],
            'Fashion': ['style', 'design', 'fashion', 'trend', 'collection', 'wear'],
            'Movies': ['film', 'movie', 'cinema', 'director', 'actor', 'hollywood'],
            'Sports': ['game', 'player', 'team', 'tournament', 'championship', 'athlete'],
            'Health': ['medical', 'health', 'wellness', 'therapy', 'treatment', 'doctor'],
            'Music': ['song', 'album', 'artist', 'band', 'concert', 'musical'],
            'Gaming': ['game', 'gaming', 'player', 'console', 'esports', 'developer'],
            'Environment': ['climate', 'environmental', 'sustainable', 'energy', 'eco'],
            'Travel': ['destination', 'tourism', 'travel', 'hotel', 'vacation', 'tour'],
            'Education': ['school', 'university', 'learning', 'student', 'teacher', 'course']
        }
        
        score = 0
        for interest in interests:
            if interest in topic_keywords:
                keywords = topic_keywords[interest]
                matches = sum(1 for keyword in keywords if keyword in text)
                score += matches * 2  # Double score for matching user interests
                
        return score

    async def get_recommendations(self, user_profile: str, feed_urls: list, user_interests: list, n_recommendations=5):
        tasks = [self.feed_parser.parse_feed(url) for url in feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for entries in results:
            if isinstance(entries, list):
                for entry in entries:
                    content = f"{entry['title']} {entry['description']}"
                    score = self.calculate_topic_score(content, user_interests)
                    all_articles.append((entry, score))
        
        # Sort by score and get top recommendations
        all_articles.sort(key=lambda x: x[1], reverse=True)
        recommendations = [article for article, _ in all_articles[:n_recommendations]]
        
        return recommendations