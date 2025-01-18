from bs4 import BeautifulSoup
import requests
import random
from datetime import datetime, timedelta
from itertools import combinations
import time
from urllib.parse import urljoin
import concurrent.futures
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebNewsEngine:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.scraping_count = 0
        self.last_scrape_time = None
        
        # News sources mapping - Add more sources as needed
        self.news_sources = {
            'Technology': [
                'https://techcrunch.com',
                'https://www.theverge.com',
                'https://www.wired.com'
            ],
            'Science': [
                'https://www.scientificamerican.com',
                'https://www.livescience.com',
                'https://www.sciencedaily.com'
            ],
            'Business': [
                'https://www.reuters.com/business',
                'https://www.cnbc.com',
                'https://www.bloomberg.com'
            ],
            'Arts': [
                'https://www.artnews.com',
                'https://news.artnet.com',
                'https://www.artforum.com'
            ],
            'Health': [
                'https://www.healthline.com/health-news',
                'https://www.medicalnewstoday.com',
                'https://www.webmd.com/news'
            ],
            'Sports': [
                'https://www.espn.com',
                'https://www.sports.yahoo.com',
                'https://www.cbssports.com'
            ],
            'Politics': [
                'https://www.politico.com',
                'https://www.thehill.com',
                'https://www.reuters.com/politics'
            ],
            'Education': [
                'https://www.edweek.org',
                'https://www.insidehighered.com',
                'https://www.chronicle.com'
            ],
            'Travel': [
                'https://www.travelandleisure.com',
                'https://www.lonelyplanet.com/articles',
                'https://www.afar.com'
            ],
            'Food': [
                'https://www.foodandwine.com',
                'https://www.bonappetit.com',
                'https://www.seriouseats.com'
            ],
            # Add these to the news_sources dictionary in WebNewsEngine class
            'Music': [
                'https://pitchfork.com',
                'https://www.rollingstone.com/music',
                'https://www.nme.com/news/music',
                'https://consequence.net/category/music'
            ],

            'Movies': [
                'https://variety.com/c/film',
                'https://deadline.com/c/film',
                'https://www.indiewire.com/c/film',
                'https://www.hollywoodreporter.com/c/movies'
            ],

            'Gaming': [
                'https://www.polygon.com',
                'https://kotaku.com',
                'https://www.eurogamer.net',
                'https://www.gamesindustry.biz'
            ],

            'Fashion': [
                'https://www.vogue.com/fashion',
                'https://wwd.com',
                'https://www.elle.com/fashion',
                'https://www.harpersbazaar.com/fashion'
            ],

            'Environment': [
                'https://www.ecowatch.com',
                'https://www.treehugger.com',
                'https://www.nationalgeographic.com/environment',
                'https://www.theguardian.com/environment'
            ]
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_scraping_status(self):
        """Return current scraping status"""
        return {
            'scraping_count': self.scraping_count,
            'last_scrape': self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            'cache_size': len(self.cache)
        }

    def _get_cached_results(self, category):
        if category in self.cache:
            timestamp, results = self.cache[category]
            if datetime.now().timestamp() - timestamp < self.cache_duration:
                return results
        return None

    def _cache_results(self, category, results):
        self.cache[category] = (datetime.now().timestamp(), results)

    def _clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)
        return text[:500]  # Limit length

    def _is_valid_article_url(self, url):
        """Check if URL likely points to an article"""
        article_indicators = ['/article/', '/story/', '/news/', '/post/']
        blacklist = ['/tag/', '/category/', '/author/', '/about/', '/contact/', '/search/']
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in article_indicators) and \
               not any(blocked in url_lower for blocked in blacklist)

    def _scrape_article(self, url):
        """Scrape individual article page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple methods to find title
            title = None
            for selector in ['h1', 'h1.article-title', 'h1.entry-title', '.article-title']:
                title = soup.select_one(selector)
                if title:
                    break
            
            if not title:
                title = soup.find('title')
            
            title = self._clean_text(title.text if title else '')
            
            # Try to find description
            description = None
            meta_desc = soup.find('meta', {'name': 'description'}) or \
                       soup.find('meta', {'property': 'og:description'})
            
            if meta_desc:
                description = meta_desc.get('content', '')
            else:
                # Try to get first paragraph
                first_p = soup.find('p')
                description = first_p.text if first_p else ''
            
            description = self._clean_text(description)
            
            # Try to find date
            date = None
            date_elements = soup.find('time') or \
                          soup.find('meta', {'property': 'article:published_time'}) or \
                          soup.find(class_=re.compile(r'date|time|publish'))
            
            if date_elements:
                date = date_elements.get('datetime') or \
                      date_elements.get('content') or \
                      date_elements.text
            
            if not date:
                date = datetime.now().isoformat()
            
            return {
                'title': title,
                'url': url,
                'description': description,
                'date': date,
                'source': url.split('/')[2]
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def _scrape_website(self, url, category, num_articles=3):
        """Scrape website for articles"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            article_links = set()
            
            # Find all links that might be articles
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Make URL absolute if it's relative
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                
                # Skip if not a valid article URL
                if not self._is_valid_article_url(href):
                    continue
                
                article_links.add(href)
            
            # Scrape articles
            for href in list(article_links)[:num_articles * 2]:  # Get extra in case some fail
                article = self._scrape_article(href)
                if article and article['title'] and article['description']:
                    article['category'] = category
                    articles.append(article)
                    
                if len(articles) >= num_articles:
                    break
                    
                time.sleep(1)  # Be nice to the server
            
            return articles[:num_articles]
            
        except Exception as e:
            logger.error(f"Error scraping website {url}: {e}")
            return []

    def _fetch_recent_articles(self, category, num_articles=3):
        """Fetch recent articles for a given category"""
        cached_results = self._get_cached_results(category)
        if cached_results:
            return cached_results[:num_articles]

        all_articles = []
        websites = self.news_sources.get(category, [])
        
        self.scraping_count += 1
        self.last_scrape_time = datetime.now()
        
        # Use thread pool for parallel scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {
                executor.submit(self._scrape_website, url, category, num_articles): url 
                for url in websites
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                articles = future.result()
                all_articles.extend(articles)

        # Sort by date and take the most recent ones
        all_articles.sort(key=lambda x: x['date'], reverse=True)
        results = all_articles[:num_articles]
        
        if results:
            self._cache_results(category, results)
            
        return results

    def get_recommendations(self, categories):
        """Get recommendations based on selected categories"""
        all_recommendations = []
        
        # Get recommendations for each individual category
        for category in categories:
            category_recommendations = self._fetch_recent_articles(category, 3)
            all_recommendations.extend(category_recommendations)
        
        # For combined recommendations, we'll look for articles that mention both categories
        combined_recommendations = []
        category_pairs = list(combinations(categories, 2))
        
        for cat1, cat2 in random.sample(category_pairs, min(len(category_pairs), 3)):
            # Search through existing articles for ones that mention both categories
            for article in all_recommendations:
                if (cat1.lower() in article['title'].lower() or cat1.lower() in article['description'].lower()) and \
                   (cat2.lower() in article['title'].lower() or cat2.lower() in article['description'].lower()):
                    combined_article = article.copy()
                    combined_article['category'] = f'{cat1} & {cat2}'
                    combined_recommendations.append(combined_article)
                    
                    if len(combined_recommendations) >= 3:
                        break
        
        all_recommendations.extend(combined_recommendations)
        return all_recommendations