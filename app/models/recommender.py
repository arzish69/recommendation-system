import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
from itertools import combinations
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

class RecommendationEngine:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key not found in environment variables")

        self.category_keywords = {
            'Technology': ['technology', 'tech', 'innovation', 'digital'],
            'Science': ['science', 'research', 'discovery', 'scientific'],
            'Business': ['business', 'finance', 'economy', 'market'],
            'Arts': ['art', 'culture', 'creative', 'design'],
            'Health': ['health', 'medical', 'wellness', 'healthcare'],
            'Sports': ['sports', 'athletics', 'games', 'fitness'],
            'Politics': ['politics', 'government', 'policy', 'elections'],
            'Education': ['education', 'learning', 'academic', 'teaching'],
            'Travel': ['travel', 'tourism', 'adventure', 'destination'],
            'Food': ['food', 'cuisine', 'cooking', 'culinary'],
            'Music': ['music', 'songs', 'concert', 'album'],
            'Movies': ['movies', 'film', 'cinema', 'entertainment'],
            'Gaming': ['gaming', 'games', 'esports', 'videogames'],
            'Fashion': ['fashion', 'style', 'trends', 'clothing'],
            'Environment': ['environment', 'climate', 'sustainability', 'eco']
        }

    def _get_cached_results(self, category):
        if category in self.cache:
            timestamp, results = self.cache[category]
            if datetime.now().timestamp() - timestamp < self.cache_duration:
                return results
        return None

    def _cache_results(self, category, results):
        self.cache[category] = (datetime.now().timestamp(), results)

    def _fetch_recent_articles(self, category, num_articles=3):
        """Fetch recent articles for a given category using NewsAPI"""
        cached_results = self._get_cached_results(category)
        if cached_results:
            return cached_results[:num_articles]

        articles = []
        keywords = self.category_keywords.get(category, [category])
        
        try:
            # Make actual API call to NewsAPI
            base_url = "https://newsapi.org/v2/everything"
            params = {
                'q': ' OR '.join(keywords),
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': 10,  # Request more articles than needed to ensure quality
                'apiKey': self.api_key
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                for article in data['articles']:
                    # Skip articles with missing data
                    if not all([article.get('title'), article.get('url'), article.get('description')]):
                        continue
                        
                    articles.append({
                        'title': article['title'],
                        'url': article['url'],
                        'description': article['description'],
                        'category': category,
                        'source': article['source'].get('name', 'Unknown Source'),
                        'date': article['publishedAt']
                    })
            
            # Cache the results
            if articles:
                self._cache_results(category, articles)
                return articles[:num_articles]
            else:
                print(f"No articles found for category: {category}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for {category}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching articles for {category}: {e}")
            return []

    def _get_combined_recommendations(self, categories, num_articles=3):
        """Get recommendations that combine multiple categories using real API calls"""
        combined_articles = []
        category_pairs = list(combinations(categories, 2))
        
        for cat1, cat2 in random.sample(category_pairs, min(len(category_pairs), num_articles)):
            try:
                # Create a combined query using keywords from both categories
                keywords1 = self.category_keywords.get(cat1, [cat1])
                keywords2 = self.category_keywords.get(cat2, [cat2])
                
                # Combine keywords with AND to find articles that mention both categories
                query = f"({' OR '.join(keywords1)}) AND ({' OR '.join(keywords2)})"
                
                base_url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # Longer timeframe for combined searches
                    'sortBy': 'relevancy',
                    'language': 'en',
                    'pageSize': 5,
                    'apiKey': self.api_key
                }
                
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok' and data.get('articles'):
                    article = data['articles'][0]  # Get the most relevant article
                    combined_articles.append({
                        'title': article['title'],
                        'url': article['url'],
                        'description': article['description'],
                        'category': f'{cat1} & {cat2}',
                        'source': article['source'].get('name', 'Unknown Source'),
                        'date': article['publishedAt']
                    })
                
            except Exception as e:
                print(f"Error fetching combined recommendations for {cat1} & {cat2}: {e}")
                continue
        
        return combined_articles
    

    # Add this method to your RecommendationEngine class

    def check_api_limits(self):
        """Check remaining API requests"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'country': 'us',
                'pageSize': 1,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params)
            
            # Extract rate limit information from headers
            requests_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            requests_limit = response.headers.get('X-RateLimit-Limit', 'Unknown')
            
            return {
                'remaining': requests_remaining,
                'limit': requests_limit,
                'status': response.status_code
            }
        except Exception as e:
            print(f"Error checking API limits: {e}")
            return {
                'remaining': 'Unknown',
                'limit': 'Unknown',
                'status': 'Error'
            }

    def get_recommendations(self, categories):
        """Get recommendations based on selected categories"""
        all_recommendations = []
        
        # Get recommendations for each individual category
        for category in categories:
            category_recommendations = self._fetch_recent_articles(category, 3)
            all_recommendations.extend(category_recommendations)
        
        # Get combined recommendations
        combined_recommendations = self._get_combined_recommendations(categories, 3)
        all_recommendations.extend(combined_recommendations)
        
        return all_recommendations