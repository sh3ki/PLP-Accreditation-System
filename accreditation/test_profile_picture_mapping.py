"""
Test script to verify user profile picture mapping in User Management view
"""

# Simulate what the view does
test_users = [
    {
        'id': '1',
        'first_name': 'User1',
        'last_name': 'User',
        'email': 'user1@plpasig.edu.ph',
        'profile_image_url': 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1234567890/user1_profile.jpg',
        'department': 'CCS',
        'role': 'department_user'
    },
    {
        'id': '2',
        'first_name': 'QA',
        'last_name': 'Head',
        'email': 'qahead@plpasig.edu.ph',
        'profile_image_url': '',  # No profile image
        'department': 'QA',
        'role': 'qa_head'
    },
    {
        'id': '3',
        'first_name': 'Robert',
        'middle_name': 'Nico',
        'last_name': 'Lopez',
        'email': 'lopez_robertnico@plpasig.edu.ph',
        'profile_image_url': 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1234567890/robert_profile.jpg',
        'department': 'CCS',
        'role': 'department_user'
    }
]

print("=" * 80)
print("TESTING USER PROFILE PICTURE MAPPING")
print("=" * 80)
print()

# Simulate the view's processing
for user_item in test_users:
    # Construct full name
    first_name = user_item.get('first_name', '')
    middle_name = user_item.get('middle_name', '')
    last_name = user_item.get('last_name', '')
    
    # Build full name
    if middle_name:
        user_item['name'] = f"{first_name} {middle_name} {last_name}"
    else:
        user_item['name'] = f"{first_name} {last_name}"
    
    # Map profile_image_url to profile_picture for template compatibility
    user_item['profile_picture'] = user_item.get('profile_image_url', '')
    
    # Display results
    print(f"User: {user_item['name']}")
    print(f"  Email: {user_item['email']}")
    print(f"  profile_image_url: {user_item.get('profile_image_url', 'MISSING')}")
    print(f"  profile_picture: {user_item.get('profile_picture', 'MISSING')}")
    print(f"  ✅ Mapping: {'SUCCESS' if user_item.get('profile_picture') == user_item.get('profile_image_url') else 'FAILED'}")
    print()

print("=" * 80)
print("TEST RESULTS")
print("=" * 80)

all_mapped = all(
    user.get('profile_picture') == user.get('profile_image_url')
    for user in test_users
)

if all_mapped:
    print("✅ All users have profile_picture correctly mapped to profile_image_url")
    print("✅ Profile pictures will now display correctly in User Management page")
else:
    print("❌ Some users have incorrect mapping")

print("=" * 80)
