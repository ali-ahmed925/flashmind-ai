"""
Streak System Verification Script
This script tests the streak logic by simulating different date scenarios.
"""

import os
import json
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import auth_service
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth_service import AuthService

def create_test_user():
    """Create a temporary test user for verification"""
    test_user_id = "test-streak-user-12345"
    test_user = {
        "id": test_user_id,
        "username": "StreakTestUser",
        "email": "test@streak.com",
        "password": "hashed_password",
        "total_xp": 100,
        "current_level": 1,
        "streak": 0,
        "decks_completed": 0,
        "cards_mastered": 0,
        "created_at": datetime.now().isoformat(),
        "last_activity_date": None
    }
    
    # Save test user
    AuthService.ensure_dir()
    filepath = os.path.join(AuthService.DATA_DIR, f"{test_user_id}.json")
    with open(filepath, 'w') as f:
        json.dump(test_user, f, indent=2)
    
    return test_user_id

def cleanup_test_user(user_id):
    """Remove test user file"""
    filepath = os.path.join(AuthService.DATA_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)

def set_last_activity_date(user_id, date_str):
    """Manually set the last_activity_date for testing"""
    user = AuthService.get_user(user_id)
    user['last_activity_date'] = date_str
    AuthService.update_user(user_id, user)

def get_user_streak(user_id):
    """Get current streak value"""
    user = AuthService.get_user(user_id)
    return user.get('streak', 0)

def run_tests():
    """Run all streak verification tests"""
    print("=" * 60)
    print("STREAK SYSTEM VERIFICATION")
    print("=" * 60)
    print()
    
    test_user_id = create_test_user()
    
    try:
        # Test 1: First activity (no previous date)
        print("Test 1: First Activity (No Previous Date)")
        print("-" * 60)
        AuthService.update_streak(test_user_id)
        streak = get_user_streak(test_user_id)
        print(f"Expected: 1 | Actual: {streak} | {'✓ PASS' if streak == 1 else '✗ FAIL'}")
        print()
        
        # Test 2: Same day activity (should not increment)
        print("Test 2: Same Day Activity (Should Stay at 1)")
        print("-" * 60)
        today = datetime.now().date().isoformat()
        set_last_activity_date(test_user_id, today)
        AuthService.update_streak(test_user_id)
        streak = get_user_streak(test_user_id)
        print(f"Expected: 1 | Actual: {streak} | {'✓ PASS' if streak == 1 else '✗ FAIL'}")
        print()
        
        # Test 3: Yesterday activity (should increment to 2)
        print("Test 3: Yesterday Activity (Should Increment to 2)")
        print("-" * 60)
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
        set_last_activity_date(test_user_id, yesterday)
        # Set initial streak to 1
        user = AuthService.get_user(test_user_id)
        user['streak'] = 1
        AuthService.update_user(test_user_id, user)
        
        AuthService.update_streak(test_user_id)
        streak = get_user_streak(test_user_id)
        print(f"Expected: 2 | Actual: {streak} | {'✓ PASS' if streak == 2 else '✗ FAIL'}")
        print()
        
        # Test 4: 3 days ago activity (should reset to 1)
        print("Test 4: 3 Days Ago Activity (Should Reset to 1)")
        print("-" * 60)
        three_days_ago = (datetime.now().date() - timedelta(days=3)).isoformat()
        set_last_activity_date(test_user_id, three_days_ago)
        # Set streak to 5 to test reset
        user = AuthService.get_user(test_user_id)
        user['streak'] = 5
        AuthService.update_user(test_user_id, user)
        
        AuthService.update_streak(test_user_id)
        streak = get_user_streak(test_user_id)
        print(f"Expected: 1 | Actual: {streak} | {'✓ PASS' if streak == 1 else '✗ FAIL'}")
        print()
        
        # Test 5: Consecutive days (simulate 7-day streak)
        print("Test 5: Consecutive Days (Simulate 7-Day Streak)")
        print("-" * 60)
        # Start with 6 days ago
        current_streak = 0
        for days_back in range(6, -1, -1):
            date = (datetime.now().date() - timedelta(days=days_back)).isoformat()
            if days_back > 0:
                # Set to previous day
                prev_date = (datetime.now().date() - timedelta(days=days_back + 1)).isoformat()
                set_last_activity_date(test_user_id, prev_date)
                user = AuthService.get_user(test_user_id)
                user['streak'] = current_streak
                AuthService.update_user(test_user_id, user)
            
            AuthService.update_streak(test_user_id)
            current_streak = get_user_streak(test_user_id)
            print(f"Day {7 - days_back}: Streak = {current_streak}")
        
        print(f"\nExpected Final: 7 | Actual: {current_streak} | {'✓ PASS' if current_streak == 7 else '✗ FAIL'}")
        print()
        
        print("=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)
        
    finally:
        # Cleanup
        cleanup_test_user(test_user_id)
        print("\nTest user cleaned up.")

if __name__ == "__main__":
    run_tests()
