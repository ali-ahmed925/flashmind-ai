import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta

class AuthService:
    DATA_DIR = 'data/users'
    
    @staticmethod
    def ensure_dir():
        os.makedirs(AuthService.DATA_DIR, exist_ok=True)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def register(username, email, password):
        AuthService.ensure_dir()
        
        # Check if user exists
        users = AuthService.get_all_users()
        if any(u.get('email') == email for u in users):
            return None, "Email already registered"
        if any(u.get('username') == username for u in users):
            return None, "Username already taken"
        
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password": AuthService.hash_password(password),
            "created_at": datetime.now().isoformat(),
            "total_xp": 0,
            "current_level": 1,
            "xp_for_next_level": 100,
            "streak": 0,
            "last_activity_date": None,
            "decks_completed": 0,
            "decks_created": 0,
            "cards_mastered": 0,
            "achievements": [],
            "deck_history": []
        }
        
        filepath = os.path.join(AuthService.DATA_DIR, f"{user_id}.json")
        with open(filepath, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        # Remove password from return
        user_data.pop('password')
        return user_data, None

    @staticmethod
    def login(email, password):
        users = AuthService.get_all_users()
        hashed = AuthService.hash_password(password)
        
        for user in users:
            if user.get('email') == email and user.get('password') == hashed:
                user.pop('password', None)
                return user, None
        
        return None, "Invalid email or password"

    @staticmethod
    def get_all_users():
        AuthService.ensure_dir()
        users = []
        for filename in os.listdir(AuthService.DATA_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(AuthService.DATA_DIR, filename), 'r') as f:
                    users.append(json.load(f))
        return users

    @staticmethod
    def get_user(user_id):
        filepath = os.path.join(AuthService.DATA_DIR, f"{user_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                user = json.load(f)
                user.pop('password', None)
                return user
        return None

    @staticmethod
    def update_user(user_id, updates):
        filepath = os.path.join(AuthService.DATA_DIR, f"{user_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                user = json.load(f)
            user.update(updates)
            with open(filepath, 'w') as f:
                json.dump(user, f, indent=2)
            user.pop('password', None)
            return user
        return None

    @staticmethod
    def calculate_level(xp):
        """Calculate level based on exponential XP formula"""
        level = 1
        xp_needed = 100
        total_xp_for_level = 0
        
        while xp >= total_xp_for_level + xp_needed:
            total_xp_for_level += xp_needed
            level += 1
            xp_needed = int(100 * (1.5 ** (level - 1)))
        
        xp_for_next = xp_needed
        return level, xp_for_next

    @staticmethod
    def add_xp(user_id, amount):
        """Add XP and handle level ups"""
        user = AuthService.get_user(user_id)
        if not user:
            return None
        
        old_level = user.get('current_level', 1)
        user['total_xp'] = user.get('total_xp', 0) + amount
        
        new_level, xp_for_next = AuthService.calculate_level(user['total_xp'])
        user['current_level'] = new_level
        user['xp_for_next_level'] = xp_for_next
        
        leveled_up = new_level > old_level
        
        AuthService.update_user(user_id, user)
        return {'user': user, 'leveled_up': leveled_up, 'new_level': new_level}

    @staticmethod
    def update_streak(user_id):
        """Update user's daily streak"""
        user = AuthService.get_user(user_id)
        if not user:
            return None
        
        today = datetime.now().date().isoformat()
        last_activity = user.get('last_activity_date')
        
        if not last_activity:
            # First activity ever
            user['streak'] = 1
            user['last_activity_date'] = today
        else:
            last_date = datetime.fromisoformat(last_activity).date()
            current_date = datetime.now().date()
            days_diff = (current_date - last_date).days
            
            if days_diff == 0:
                # Same day, no change
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                user['streak'] = user.get('streak', 0) + 1
                user['last_activity_date'] = today
            else:
                # Streak broken, reset to 1
                user['streak'] = 1
                user['last_activity_date'] = today
        
        AuthService.update_user(user_id, user)
        return user

    @staticmethod
    def complete_deck(user_id, deck_name, cards_count):
        """Handle deck completion: update counters, add XP, update streak"""
        user = AuthService.get_user(user_id)
        if not user:
            return None
        
        # Update counters
        user['decks_completed'] = user.get('decks_completed', 0) + 1
        user['cards_mastered'] = user.get('cards_mastered', 0) + cards_count
        
        # Add to deck history
        if 'deck_history' not in user:
            user['deck_history'] = []
        
        user['deck_history'].append({
            'name': deck_name,
            'cards_count': cards_count,
            'completed_at': datetime.now().isoformat()
        })
        
        # Update streak
        AuthService.update_user(user_id, user)
        user = AuthService.update_streak(user_id)
        
        # Add XP (10 per card)
        xp_result = AuthService.add_xp(user_id, cards_count * 10)
        
        return xp_result

    @staticmethod
    def increment_decks_created(user_id, deck_name, cards_count, difficulty):
        """Increment decks created counter"""
        user = AuthService.get_user(user_id)
        if not user:
            return None
        
        user['decks_created'] = user.get('decks_created', 0) + 1
        
        AuthService.update_user(user_id, user)
        return user

    @staticmethod
    def get_leaderboard():
        """Get all users ranked by total XP"""
        users = AuthService.get_all_users()
        
        # Remove sensitive data and prepare for leaderboard
        leaderboard_users = []
        for user in users:
            leaderboard_users.append({
                'id': user.get('id'),
                'username': user.get('username'),
                'total_xp': user.get('total_xp', 0),
                'current_level': user.get('current_level', 1),
                'streak': user.get('streak', 0),
                'decks_completed': user.get('decks_completed', 0)
            })
        
        # Sort by total_xp descending
        leaderboard_users.sort(key=lambda x: x['total_xp'], reverse=True)
        
        # Add rank numbers
        for idx, user in enumerate(leaderboard_users):
            user['rank'] = idx + 1
        
        return leaderboard_users
