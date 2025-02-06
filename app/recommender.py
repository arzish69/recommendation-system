# recommender.py
from .feed_parser import FeedParser
from urllib.parse import urlparse
import torch
import asyncio
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class EnhancedRecommender:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModel.from_pretrained('bert-base-uncased').to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.feed_parser = FeedParser()

    def generate_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Reshape to ensure 2D array
        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        return embedding.reshape(1, -1)

    async def get_recommendations(self, user_profile: str, feed_urls: list, n_recommendations=5):
        all_entries = []
        
        # Fetch from all sources concurrently
        tasks = [self.feed_parser.parse_feed(url) for url in feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for entries in results:
            if isinstance(entries, list):  # Skip failed feeds
                all_entries.extend(entries)

        if not all_entries:
            return []

        # Ensure source diversity
        source_groups = {}
        for entry in all_entries:
            source = urlparse(entry['link']).netloc
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(entry)

        # Get embeddings and similarities for each source group
        recommendations = []
        sources = list(source_groups.keys())
        np.random.shuffle(sources)  # Randomize source order
        
        user_embedding = self.generate_embedding(user_profile)
        
        while len(recommendations) < n_recommendations and sources:
            source = sources.pop(0)
            entries = source_groups[source]
            
            if not entries:
                continue
                
            # Get top entry from this source
            embeddings = np.vstack([
                self.generate_embedding(f"{e['title']} {e['description']}")
                for e in entries
            ])
            
            similarities = cosine_similarity(user_embedding, embeddings)[0]
            best_idx = similarities.argmax()
            
            recommendations.append(entries[best_idx])
            # Remove selected entry
            entries.pop(best_idx)
            
            # Put source back if it has more entries
            if entries:
                sources.append(source)

        return recommendations