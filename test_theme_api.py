import requests
import json

BASE_URL = 'http://localhost:5000'
SESSION = requests.Session()

def login(username, password):
    print(f"Logging in as {username}...")
    response = SESSION.post(f'{BASE_URL}/admin/login', json={
        'username': username,
        'password': password
    })
    if response.status_code == 200 and response.json().get('success'):
        print("Login successful")
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

def get_theme():
    print("Fetching theme settings...")
    response = SESSION.get(f'{BASE_URL}/api/theme/settings')
    if response.status_code == 200:
        theme = response.json()
        print(f"Current theme font: {theme.get('font')}")
        return theme
    else:
        print(f"Failed to get theme: {response.text}")
        return None

def update_theme(new_color):
    print(f"Updating theme primary color to {new_color}...")
    # First get current theme to preserve other settings
    current_theme = get_theme()
    if not current_theme:
        return False
        
    current_theme['colors']['primary'] = new_color
    current_theme['colors']['sidebar_text'] = '#123456'
    
    response = SESSION.post(f'{BASE_URL}/api/theme/settings', json=current_theme)
    if response.status_code == 200:
        print("Theme updated successfully")
        return True
    else:
        print(f"Failed to update theme: {response.text}")
        return False

def update_logo():
    print("Testing logo settings update...")
    current_theme = get_theme()
    if not current_theme:
        return False
    
    current_theme['logo'] = {
        'type': 'image',
        'text': 'Test Logo',
        'url': '/static/uploads/test_logo.png'
    }
    
    response = SESSION.post(f'{BASE_URL}/api/theme/settings', json=current_theme)
    if response.status_code == 200:
        print("Logo settings updated successfully")
        # Verify
        updated_theme = get_theme()
        if updated_theme['logo']['type'] == 'image' and updated_theme['logo']['url'] == '/static/uploads/test_logo.png':
            print("Verification: Logo settings persisted correctly")
            return True
        else:
            print("Verification FAILED: Logo settings not persisted")
            return False
    else:
        print(f"Failed to update logo settings: {response.text}")
        return False

def check_css(expected_color):
    print("Checking dynamic CSS...")
    response = requests.get(f'{BASE_URL}/custom-theme.css')
    if response.status_code == 200:
        css_content = response.text
        if expected_color in css_content and '#123456' in css_content:
            print(f"Verification: CSS contains expected color {expected_color} and sidebar text #123456")
            return True
        else:
            print(f"Verification FAILED: CSS missing colors")
            return False
    else:
        print(f"Failed to get CSS: {response.status_code}")
        return False

def reset_theme():
    print("Resetting theme...")
    response = SESSION.post(f'{BASE_URL}/api/theme/reset')
    if response.status_code == 200:
        print("Theme reset successfully")
        return True
    else:
        print(f"Failed to reset theme: {response.text}")
        return False

def run_tests():
    # 1. Login
    if not login('admin', 'admin'):
        return

    # 2. Get initial theme
    get_theme()

    # 3. Update theme
    test_color = '#FF5733'
    if update_theme(test_color):
        # 4. Verify CSS
        check_css(test_color)

    # 4.5 Test Logo Update
    update_logo()

    # 5. Reset theme
    if reset_theme():
        # Verify reset (should not have test_color)
        print("Verifying reset...")
        response = requests.get(f'{BASE_URL}/custom-theme.css')
        if test_color not in response.text:
             print("Verification: Theme reset confirmed")
        else:
             print("Verification FAILED: Theme still has test color")

if __name__ == '__main__':
    try:
        run_tests()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the server is running on http://localhost:5000")
