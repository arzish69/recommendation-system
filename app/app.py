# app.py
from fastapi import FastAPI, HTTPException, Depends, Header
from firebase_admin import auth
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from app.recommender import BasicRecommender

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = BasicRecommender()

async def get_current_user(authorization: str = Header(None)):
    """Basic Firebase auth middleware with better error handling"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    try:
        token = authorization.replace('Bearer ', '')
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication: {str(e)}"
        )

@app.get("/api/recommendations")
async def get_recommendations(user_id: str = Depends(get_current_user)):
    try:
        # Get user's links
        user_links = await recommender.get_user_links(user_id)
        if not user_links:
            return {"recommendations": [], "message": "No user links found"}
            
        # Get candidate links from other users
        candidate_links = await recommender.get_other_users_links(user_id)
        if not candidate_links:
            return {"recommendations": [], "message": "No candidate links found"}
        
        # Generate recommendations
        recommendations = recommender.get_recommendations(user_links, candidate_links)
        
        return {
            "recommendations": recommendations,
            "user_links_count": len(user_links),
            "candidate_links_count": len(candidate_links)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

# Add a root endpoint for health check
@app.get("/")
async def root():
    return {"status": "ok"}