# feed_manager.py
from typing import List, Dict

class FeedManager:
    def __init__(self):
        self.feed_sources = {
            "Technology": [
                "https://feeds.feedburner.com/TechCrunch",
                "https://www.wired.com/feed/rss",
                "https://www.theverge.com/rss/index.xml"
            ],
            "Science": [
                "https://www.sciencedaily.com/rss/all.xml",
                "https://www.nature.com/nature.rss",
                "https://www.newscientist.com/feed/home/"
            ],
            "Business": [
                "https://www.forbes.com/real-time/feed2/",
                "https://www.ft.com/world?format=rss",
                "https://feeds.bloomberg.com/markets/news.rss"
            ],
            "Arts": [
                "https://www.artnews.com/feed",
                "https://www.artforum.com/rss",
                "https://www.artsy.net/rss"
            ],
            "Politics": [
                "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
                "https://feeds.washingtonpost.com/rss/politics",
                "https://www.politico.com/rss/politics.xml"
            ],
            "Food": [
                "https://www.foodandwine.com/feed",
                "https://www.bonappetit.com/feed/rss",
                "https://www.seriouseats.com/feeds/all"
            ],
            "Fashion": [
                "https://www.vogue.com/feed",
                "https://www.elle.com/rss",
                "https://www.harpersbazaar.com/rss"
            ],
            "Movies": [
                "https://www.variety.com/feed",
                "https://www.hollywoodreporter.com/feed",
                "https://deadline.com/feed"
            ],
            "Sports": [
                "https://www.espn.com/espn/rss/news",
                "https://rss.cbc.ca/lineup/sports.xml",
                "https://www.sports.yahoo.com/rss"
            ],
            "Health": [
                "https://www.health.com/feed",
                "https://rss.medicalnewstoday.com/featurednews.xml",
                "https://www.webmd.com/rss/default.xml"
            ],
            "Music": [
                "https://www.rollingstone.com/music/feed",
                "https://pitchfork.com/rss",
                "https://www.billboard.com/feed"
            ],
            "Gaming": [
                "https://www.ign.com/rss/articles",
                "https://www.gamespot.com/feeds/news",
                "https://www.polygon.com/rss/index.xml"
            ],
            "Environment": [
                "https://www.nationalgeographic.com/environment/feed",
                "https://www.ecowatch.com/feed",
                "https://www.treehugger.com/feeds/all.rss"
            ],
            "Travel": [
                "https://www.lonelyplanet.com/blog/feed",
                "https://www.travelandleisure.com/feeds/all",
                "https://www.afar.com/rss"
            ],
            "Education": [
                "https://www.edweek.org/feed",
                "https://www.chronicle.com/rss",
                "https://www.insidehighered.com/feed"
            ]
        }

    def get_feeds_for_interests(self, user_interests: List[str]) -> List[str]:
        """
        Get feed URLs based on user interests.
        Args:
            user_interests: List of user's interest categories
        Returns:
            List of feed URLs
        """
        feed_urls = []
        for interest in user_interests:
            if interest in self.feed_sources:
                feed_urls.extend(self.feed_sources[interest])
        return feed_urls