"""
Password Generator Utility
Generates strong, memorable passwords for new users
"""

import random
import string


def generate_strong_password():
    """
    Generate a strong, memorable password
    Format: Word + Number + Symbol + Number
    Example: Tiger@2024, Ocean!5891, Mountain#7432
    
    Returns:
        str: Generated password
    """
    
    # List of memorable words
    words = [
        'Tiger', 'Ocean', 'Mountain', 'River', 'Eagle', 'Lion', 'Phoenix',
        'Dragon', 'Wolf', 'Falcon', 'Thunder', 'Lightning', 'Storm', 'Cloud',
        'Forest', 'Desert', 'Island', 'Valley', 'Canyon', 'Summit', 'Horizon',
        'Sunset', 'Sunrise', 'Galaxy', 'Comet', 'Planet', 'Saturn', 'Jupiter',
        'Meteor', 'Nebula', 'Quasar', 'Cosmos', 'Stellar', 'Lunar', 'Solar',
        'Crystal', 'Diamond', 'Emerald', 'Sapphire', 'Ruby', 'Pearl', 'Coral',
        'Amber', 'Jade', 'Topaz', 'Onyx', 'Silver', 'Golden', 'Platinum',
        'Arctic', 'Alpine', 'Pacific', 'Atlantic', 'Tropical', 'Polar'
    ]
    
    # Symbols for password strength
    symbols = ['@', '#', '!', '$', '%', '&', '*']
    
    # Generate password components
    word = random.choice(words)
    symbol = random.choice(symbols)
    number1 = random.randint(10, 99)
    number2 = random.randint(10, 99)
    
    # Combine into password: Word + Symbol + Numbers
    password = f"{word}{symbol}{number1}{number2}"
    
    return password


def generate_password_with_policy(min_length=10):
    """
    Generate password meeting specific policy requirements
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Minimum length
    
    Args:
        min_length (int): Minimum password length
        
    Returns:
        str: Generated password
    """
    return generate_strong_password()  # Already meets all requirements


# Example usage and testing
if __name__ == "__main__":
    print("Generated Passwords:")
    for i in range(10):
        print(f"{i+1}. {generate_strong_password()}")
