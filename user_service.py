import os
import json
import uuid

class UserService:
    DATA_DIR = 'data/users'
    
    @staticmethod
    def ensure_user_dir():
        os.makedirs(UserService.DATA_DIR, exist_ok=True)

    @staticmethod
    def create_user(username):
        UserService.ensure_user_dir()
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": username,
            "xp": 0,
            "level": 1,
            "streak": 0,
            "decks_completed": 0,
            "achievements": []
        }
        UserService.save_user(user_data)
        return user_data

    @staticmethod
    def get_user(user_id):
        filepath = os.path.join(UserService.DATA_DIR, f"{user_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

    @staticmethod
    def save_user(user_data):
        UserService.ensure_user_dir()
        filepath = os.path.join(UserService.DATA_DIR, f"{user_data['id']}.json")
        with open(filepath, 'w') as f:
            json.dump(user_data, f)
            
    @staticmethod
    def add_xp(user_id, amount):
        user = UserService.get_user(user_id)
        if user:
            user['xp'] += amount
            # Simple level up logic: Level = 1 + (XP / 1000)
            user['level'] = 1 + (user['xp'] // 1000)
            UserService.save_user(user)
            return user
        return None
