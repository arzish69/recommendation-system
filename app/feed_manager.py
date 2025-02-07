# feed_manager.py
from typing import List, Dict

class FeedManager:
    def __init__(self):
        self.feed_sources = {
            "Technology": [
                "https://feeds.feedburner.com/TechCrunch",
                "https://www.wired.com/feed/rss",
                "https://www.theverge.com/rss/index.xml",
                "https://www.technologyreview.com/feed/atom/", # Atom
                "https://www.engadget.com/rss.xml" # RSS (Engadget's primary is RSS, using it as backup if atom hard to find and relevant)
            ],
            "Science": [
                "https://www.sciencedaily.com/rss/all.xml",
                "https://www.nature.com/nature.rss",
                "https://www.newscientist.com/feed/home/",
                "https://www.sciencemag.org/rss/current_news.xml", # RSS (ScienceMag's primary is RSS, using it as backup if atom hard to find and relevant)
                "https://phys.org/rss-feed/" # RSS (Phys.org's primary is RSS, using it as backup if atom hard to find and relevant)
            ],
            "Business": [
                "https://www.forbes.com/real-time/feed2/",
                "https://www.ft.com/world?format=rss",
                "https://feeds.bloomberg.com/markets/news.rss",
                 "https://www.economist.com/finance-and-economics/rss.xml", # RSS (Economist finance section RSS as Atom hard to find generally for broad business)
                 "https://hbr.org/rss/featured" # RSS (HBR featured articles RSS, good business content, Atom harder to find)
            ],
            "Arts": [
                "https://www.artnews.com/feed",
                "https://www.artforum.com/rss",
                "https://www.artsy.net/rss",
                "http://feeds.feedburner.com/hyperallergic", # RSS (Hyperallergic, good arts blog, RSS as Atom harder to find)
                "https://news.artnet.com/feed" # RSS (Artnet news, RSS as Atom harder to find for general art news)
            ],
            "Politics": [
                "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
                "https://feeds.washingtonpost.com/rss/politics",
                "https://www.politico.com/rss/politics.xml",
                "https://www.cfr.org/taxonomy/term/4/feed", # RSS (Council on Foreign Relations, good for policy/politics, RSS as Atom harder to find)
                "https://www.bbc.co.uk/news/politics/rss.xml" # RSS (BBC Politics, widely respected, RSS as Atom harder to find)
            ],
            "Food": [
                "https://www.foodandwine.com/feed",
                "https://www.bonappetit.com/feed/rss",
                "https://www.seriouseats.com/feeds/all",
                "https://www.simplyrecipes.com/feed/", # RSS (Simply Recipes, popular recipe site, RSS as Atom harder to find for food blogs)
                "https://smittenkitchen.com/feed/" # RSS (Smitten Kitchen, popular food blog, RSS as Atom harder to find for food blogs)
            ],
            "Fashion": [
                "https://www.vogue.com/feed",
                "https://www.elle.com/rss",
                "https://www.harpersbazaar.com/rss",
                "https://fashionista.com/.rss" # RSS (Fashionista, fashion industry news, RSS as Atom harder to find)
                ,"https://wwd.com/feed/" # RSS (WWD, Women's Wear Daily, fashion business, RSS as Atom harder to find)
            ],
            "Movies": [
                "https://www.variety.com/feed",
                "https://www.hollywoodreporter.com/feed",
                "https://deadline.com/feed",
                "https://www.indiewire.com/feed/", # RSS (IndieWire, independent film focus, RSS as Atom harder to find)
                "https://www.empireonline.com/feeds/rss/" # RSS (Empire Online, movie magazine, RSS as Atom harder to find)
            ],
            "Sports": [
                "https://www.espn.com/espn/rss/news",
                "https://rss.cbc.ca/lineup/sports.xml",
                "https://www.sports.yahoo.com/rss",
                "https://www.si.com/rss/si_topstories.rss", # RSS (Sports Illustrated, general sports news, RSS as Atom harder to find)
                "https://syndication. BleacherReport.com/rss/media_items/10.rss" # RSS (Bleacher Report, broad sports coverage, using RSS as Atom is less common in sports news)
            ],
            "Health": [
                "https://www.health.com/feed",
                "https://rss.medicalnewstoday.com/featurednews.xml",
                "https://www.webmd.com/rss/default.xml",
                "https://www.mayoclinic.org/patient-care-and-health-information/news-events/rss/DASH", # RSS (Mayo Clinic News, reputable health info, RSS as Atom harder to find)
                "https://www.nhs.uk/news/Pages/NewsArticles.aspx?rss=true" # RSS (NHS News, UK's National Health Service, RSS as Atom harder to find in official health news)
            ],
            "Music": [
                "https://www.rollingstone.com/music/feed",
                "https://pitchfork.com/rss",
                "https://www.billboard.com/feed",
                "https://consequence.net/feed/" # RSS (Consequence of Sound, music and culture site, RSS as Atom harder to find)
                ,"https://www.nme.com/rss.xml" # RSS (NME, music news and reviews, RSS as Atom harder to find)
            ],
            "Gaming": [
                "https://www.ign.com/rss/articles",
                "https://www.gamespot.com/feeds/news",
                "https://www.polygon.com/rss/index.xml",
                "https://kotaku.com/rss" # RSS (Kotaku, gaming news and culture, RSS as Atom harder to find)
                ,"https://www.pcgamer.com/rss/" # RSS (PC Gamer, PC gaming focused, RSS as Atom harder to find)
            ],
            "Environment": [
                "https://www.nationalgeographic.com/environment/feed",
                "https://www.ecowatch.com/feed",
                "https://www.treehugger.com/feeds/all.rss",
                "https://grist.org/feed/" # RSS (Grist, environmental news and solutions, RSS as Atom harder to find)
                ,"https://www.theguardian.com/environment/rss" # RSS (Guardian Environment section, reputable news source, RSS as Atom harder to find)
            ],
            "Travel": [
                "https://www.lonelyplanet.com/blog/feed",
                "https://www.travelandleisure.com/feeds/all",
                "https://www.afar.com/rss",
                "https://www.cntraveler.com/feed/rss" # RSS (Conde Nast Traveler, luxury travel, RSS as Atom harder to find)
                ,"https://www.nomadicmatt.com/feed/" # RSS (Nomadic Matt, popular travel blog, RSS as Atom harder to find for blogs)
            ],
            "Education": [
                "https://www.edweek.org/feed",
                "https://www.chronicle.com/rss",
                "https://www.insidehighered.com/feed",
                "https://www.timeshighereducation.com/feeds/rss.xml" # RSS (Times Higher Education, higher ed news, RSS as Atom harder to find)
                ,"https://hechingerreport.org/feed/" # RSS (Hechinger Report, education news, RSS as Atom harder to find)
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