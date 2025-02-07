from .feed_parser import FeedParser
from datetime import datetime, timedelta
import asyncio

class TopicBasedRecommender:
    def __init__(self):
        self.feed_parser = FeedParser()

    def calculate_topic_score(self, text, interests, published_date_str):
        text = text.lower()
        topic_keywords = {
            'Technology': ['tech', 'software', 'digital', 'ai', 'computer', 'app', 'cyber', 'innovation', 'programming', 'gadget', 'electronics', 'internet'],
            'Science': ['research', 'study', 'scientist', 'discovery', 'lab', 'physics', 'chemistry', 'biology', 'astronomy', 'experiment', 'scientific'],
            'Business': ['market', 'company', 'startup', 'finance', 'industry', 'trade', 'economy', 'investment', 'business', 'entrepreneur', 'commerce'],
            'Arts': ['artist', 'exhibition', 'museum', 'gallery', 'painting', 'sculpture', 'art', 'design', 'creative', 'artwork', 'culture'],
            'Politics': ['government', 'policy', 'election', 'congress', 'political', 'vote', 'democracy', 'president', 'legislation', 'campaign', 'civic'],
            'Food': ['recipe', 'restaurant', 'cuisine', 'cooking', 'chef', 'meal', 'food', 'dining', 'ingredients', 'gourmet', 'culinary'],
            'Fashion': ['style', 'design', 'fashion', 'trend', 'collection', 'wear', 'clothing', 'apparel', 'luxury', 'couture', 'stylish'],
            'Movies': ['film', 'movie', 'cinema', 'director', 'actor', 'hollywood', 'screen', 'drama', 'comedy', 'thriller', 'animation'],
            'Sports': ['game', 'player', 'team', 'tournament', 'championship', 'athlete', 'sport', 'football', 'basketball', 'soccer', 'tennis'],
            'Health': ['medical', 'health', 'wellness', 'therapy', 'treatment', 'doctor', 'disease', 'medicine', 'healthcare', 'fitness', 'nutrition'],
            'Music': ['song', 'album', 'artist', 'band', 'concert', 'musical', 'music', 'genre', 'melody', 'rhythm', 'lyrics'],
            'Gaming': ['game', 'gaming', 'player', 'console', 'esports', 'developer', 'videogame', 'pc', 'playstation', 'xbox', 'nintendo'],
            'Environment': ['climate', 'environmental', 'sustainable', 'energy', 'eco', 'nature', 'pollution', 'conservation', 'planet', 'ecology', 'green'],
            'Travel': ['destination', 'tourism', 'travel', 'hotel', 'vacation', 'tour', 'adventure', 'explore', 'holiday', 'journey', 'trip'],
            'Education': ['school', 'university', 'learning', 'student', 'teacher', 'course', 'education', 'knowledge', 'study', 'academic', 'college']
        }

        score = 0
        for interest in interests:
            if interest in topic_keywords:
                keywords = topic_keywords[interest]
                matches = sum(1 for keyword in keywords if keyword in text)
                score += matches * 2

        if published_date_str:
            try:
                published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
                now = datetime.now()
                age_days = (now - published_date).days
                freshness_bonus = 0
                if age_days <= 7:
                    freshness_bonus = 5
                elif age_days <= 14:
                    freshness_bonus = 3
                elif age_days <= 30:
                    freshness_bonus = 1
                score += freshness_bonus
            except (ValueError, AttributeError, TypeError):
                pass
        return score

    def is_within_date_range(self, article_date_str):
        try:
            article_date = datetime.fromisoformat(article_date_str.replace('Z', '+00:00'))
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            return one_month_ago <= article_date <= today
        except (ValueError, AttributeError, TypeError):
            return False

    def is_valid_article(self, article):
        if not article.get('description') or len(article['description'].strip()) == 0:
            return False
        if not article.get('thumbnail'):
            return False
        if not article.get('title') or len(article['title'].strip()) == 0:
            return False
        if not article.get('link') or len(article['link'].strip()) == 0:
            return False
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
                    if self.is_valid_article(entry):
                        content = f"{entry['title']} {entry['description']}"
                        score = self.calculate_topic_score(content, user_interests, entry.get('published'))
                        all_articles.append((entry, score))

        all_articles.sort(key=lambda x: x[1], reverse=True)
        recommendations = [article for article, _ in all_articles[:n_recommendations]]
        return recommendations

    async def close(self):
        await self.feed_parser.close()