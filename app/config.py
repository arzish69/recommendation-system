import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CATEGORIES = [
        {'id': 1, 'name': 'Technology', 'icon': '💻'},
        {'id': 2, 'name': 'Science', 'icon': '🔬'},
        {'id': 3, 'name': 'Business', 'icon': '💼'},
        {'id': 4, 'name': 'Arts', 'icon': '🎨'},
        {'id': 5, 'name': 'Health', 'icon': '🏥'},
        {'id': 6, 'name': 'Sports', 'icon': '⚽'},
        {'id': 7, 'name': 'Politics', 'icon': '🏛️'},
        {'id': 8, 'name': 'Education', 'icon': '📚'},
        {'id': 9, 'name': 'Travel', 'icon': '✈️'},
        {'id': 10, 'name': 'Food', 'icon': '🍳'},
        { id: 11, 'name': 'Music', 'icon': '🎵' },
        { id: 12, 'name': 'Movies', 'icon': '🎬' },
        { id: 13, 'name': 'Gaming', 'icon': '🎮' },
        { id: 14, 'name': 'Fashion', 'icon': '👗' },
        { id: 15, 'name': 'Environment', 'icon': '🌍' }
    ]