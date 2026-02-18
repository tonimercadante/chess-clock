#!/usr/bin/env python
import os
import sys
import django

# Add project root to sys.path if running from scripts/seeds
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chessclock.settings")
django.setup()

# Use the custom user model
from django.contrib.auth import get_user_model
User = get_user_model()

def create_normal_users():
    users = [
        {'username': 'alice', 'password': 'pass123'},
        {'username': 'bob', 'password': 'pass456'},
    ]
    for u in users:
        if not User.objects.filter(username=u['username']).exists():
            User.objects.create_user(username=u['username'], password=u['password'])
            print(f"Created user {u['username']}")
        else:
            print(f"User {u['username']} already exists")

if __name__ == "__main__":
    create_normal_users()

