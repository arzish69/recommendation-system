# app.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials, auth
from typing import List, Optional
from .recommender import EnhancedRecommender

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Firebase initialization
cred = credentials.Certificate('service_acc.json')
initialize_app(cred)

recommender = EnhancedRecommender()

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.replace('Bearer ', '')
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations(
    user_profile: str = "Default user profile",
    feed_urls: Optional[List[str]] = None,
    user_id: str = Depends(get_current_user)
):
    if not feed_urls:
        feed_urls = [
            "https://techcrunch.com/feed/",
            "https://news.ycombinator.com/rss",
            "https://feeds.feedburner.com/TheHackersNews",
            "https://www.wired.com/feed/rss",
            "https://www.theverge.com/rss/index.xml"
        ]

    try:
        recommendations = await recommender.get_recommendations(
            user_profile,
            feed_urls
        )
        return {
            "recommendations": recommendations,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.on_event("shutdown")
async def shutdown_event():
    await recommender.close()

@app.get("/")
async def root():
    return {"status": "ok"}