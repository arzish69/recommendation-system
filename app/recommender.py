from .feed_parser import FeedParser
from urllib.parse import urlparse
import asyncio
from collections import Counter
import re
from datetime import datetime, timedelta

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

    def is_within_date_range(self, article_date_str):
        """
        Check if the article's date is within the last month.
        
        Args:
            article_date_str (str): ISO format date string
            
        Returns:
            bool: True if article is within date range, False otherwise
        """
        try:
            # Parse the article date
            article_date = datetime.fromisoformat(article_date_str.replace('Z', '+00:00'))
            
            # Get today's date and the date from one month ago
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            
            # Check if article date is between one month ago and today
            return one_month_ago <= article_date <= today
        except (ValueError, AttributeError, TypeError):
            # If there's any error parsing the date, exclude the article
            return False

    def is_valid_article(self, article):
        """
        Validate if an article has all required fields with meaningful content
        and is within the acceptable date range.
        
        Args:
            article (dict): Article dictionary containing metadata
            
        Returns:
            bool: True if article has all required fields and is recent, False otherwise
        """
        # Check if description exists and is not empty
        if not article.get('description') or len(article['description'].strip()) == 0:
            return False
            
        # Check if thumbnail exists and is not None or empty
        if not article.get('thumbnail'):
            return False
            
        # Check if title exists and is not empty
        if not article.get('title') or len(article['title'].strip()) == 0:
            return False
            
        # Check if link exists and is not empty
        if not article.get('link') or len(article['link'].strip()) == 0:
            return False
            
        # Check if published date exists and is within range
        if not article.get('published'):
            return False
            
        return self.is_within_date_range(article['published'])

    async def get_recommendations(self, user_profile: str, feed_urls: list, user_interests: list, n_recommendations=5):
        tasks = [self.feed_parser.parse_feed(url) for url in feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for entries in results:
            if isinstance(entries, list):
                for entry in entries:
                    # Only process articles that have all required fields and are recent
                    if self.is_valid_article(entry):
                        content = f"{entry['title']} {entry['description']}"
                        score = self.calculate_topic_score(content, user_interests)
                        all_articles.append((entry, score))
        
        # Sort by score and get top recommendations
        all_articles.sort(key=lambda x: x[1], reverse=True)
        recommendations = [article for article, _ in all_articles[:n_recommendations]]
        
        return recommendations

    async def close(self):
        await self.feed_parser.close()