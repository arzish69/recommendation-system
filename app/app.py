from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials, firestore, auth, _apps
from typing import List, Optional
from app.recommender import TopicBasedRecommender
from app.feed_manager import FeedManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not _apps:
    cred = credentials.Certificate("service_acc.json")
    initialize_app(cred)

db = firestore.client()

recommender = TopicBasedRecommender()
feed_manager = FeedManager()

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.replace('Bearer ', '')
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']

        # Fetch user interests from Firestore
        user_ref = db.collection('users').document(uid)
        user_data = user_ref.get()

        if not user_data.exists:
            raise HTTPException(status_code=404, detail="User not found")

        interests = user_data.to_dict().get("interests", [])

        return {"uid": uid, "interests": interests}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
    

@app.get("/api/recommendations")
async def get_recommendations(
    user_profile: str = "General interest reader",
    feed_urls: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user)
):
    if not feed_urls:
        feed_urls = feed_manager.get_feeds_for_interests(current_user['interests'])

    try:
        recommendations = await recommender.get_recommendations(
            user_profile,
            feed_urls,
            current_user['interests']
        )
        return {
            "recommendations": recommendations,
            "user_id": current_user['uid'],
            "interests": current_user['interests'],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    await recommender.close()

@app.get("/")
async def root():
    return {"status": "ok"}