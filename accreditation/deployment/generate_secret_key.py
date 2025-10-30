#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Django production
Run this and copy the output to your .env file
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("=" * 80)
    print("GENERATED SECRET KEY FOR PRODUCTION")
    print("=" * 80)
    print(f"\nSECRET_KEY={secret_key}\n")
    print("=" * 80)
    print("Copy the line above and paste it into your .env file on the server")
    print("=" * 80)
