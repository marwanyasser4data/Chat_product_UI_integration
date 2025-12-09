"""
Flask Chat Application
Modern chatbot interface without Chainlit
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from functools import wraps
from agent import chat_agent
import uuid
import secrets
import json
from datetime import datetime
import os
from dotenv import load_dotenv, set_key, find_dotenv
from werkzeug.utils import secure_filename
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User credentials and roles
USERS = {
    'admin': {
        'password': 'admin',
        'role': 'admin',
        'name': 'المدير'
    },
    'user': {
        'password': 'user',
        'role': 'user',
        'name': 'مستخدم'
    }
}

# In-memory storage for chat history (use database in production)
chat_sessions = {}

# Helper Functions
def load_users():
    """Load users from JSON file"""
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return USERS

def save_users(users_data):
    """Save users to JSON file"""
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

def load_theme_settings():
    """Load theme settings from JSON file"""
    default_theme = {
        'colors': {
            'primary': '#00A651',
            'primary_dark': '#008542',
            'primary_light': '#E8F5E9',
            'secondary': '#1E88E5',
            'background': '#F5F7FA',
            'sidebar': '#FAFBFC',
            'sidebar_text': '#1A1D1F',
            'text_primary': '#1A1D1F',
            'text_secondary': '#6F7782',
            'user_msg_bg': '#F0F4F8',
            'bot_msg_bg': '#FFFFFF',
            'ai_badge_bg': '#00A651'
        },
        'font': 'Cairo',
        'app_name': {
            'ar': 'نموذج الذكاء الاصطناعي للبيانات',
            'en': 'DataScience LLM Chat Model'
        },
        'chat_header_title': {
            'ar': 'مساعد الذكاء الاصطناعي',
            'en': 'AI Assistant'
        },
        'logo': {
            'type': 'text',
            'text': 'DS',
            'url': ''
        },
        'background_image': ''
    }
    
    if os.path.exists('theme.json'):
        try:
            with open('theme.json', 'r', encoding='utf-8') as f:
                saved_theme = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_theme.items():
                    if key not in saved_theme:
                        saved_theme[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in saved_theme[key]:
                                saved_theme[key][subkey] = subvalue
                return saved_theme
        except:
            return default_theme
    return default_theme

def save_theme_settings(settings):
    """Save theme settings to JSON file"""
    with open('theme.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def get_current_theme():
    """Get current theme name from .env"""
    return os.getenv('APP_THEME', 'nhc')

def save_theme_to_env(theme):
    """Save theme preference to .env file"""
    env_file = find_dotenv()
    if not env_file:
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                pass
    set_key(env_file, 'APP_THEME', theme)

def load_settings_from_env():
    """Load settings from .env file"""
    return {
        'provider': os.getenv('LLM_PROVIDER', 'fake'),
        'model': os.getenv('LLM_MODEL', 'gpt-4o'),
        'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2000')),
        'api_key': os.getenv('LLM_API_KEY', '')
    }

def save_settings_to_env(settings):
    """Save settings to .env file"""
    env_file = find_dotenv()
    if not env_file:
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                pass
    
    set_key(env_file, 'LLM_PROVIDER', settings['provider'])
    set_key(env_file, 'LLM_MODEL', settings['model'])
    set_key(env_file, 'LLM_TEMPERATURE', str(settings['temperature']))
    set_key(env_file, 'LLM_MAX_TOKENS', str(settings['max_tokens']))
    if settings.get('api_key'):
        set_key(env_file, 'LLM_API_KEY', settings['api_key'])

# Initialize users
USERS = load_users()

# Update chat agent with loaded settings
DEFAULT_SETTINGS = load_settings_from_env()
chat_agent.update_config(DEFAULT_SETTINGS)

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Check if it's an AJAX request
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
            return redirect(url_for('login_page'))
        if session.get('role') != 'admin':
            return jsonify({'error': 'غير مصرح لك بالوصول'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/login')
def login_page():
    """Redirect to main page - auto-login enabled"""
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        users = load_users()
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            session['user_display_name'] = users[username]['name']
            
            return jsonify({
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'role': users[username]['role']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في تسجيل الدخول'
        }), 500

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set user language preference"""
    try:
        data = request.get_json()
        lang = data.get('language', 'ar')
        if lang in ['ar', 'en']:
            session['language'] = lang
            return jsonify({'success': True, 'language': lang})
        return jsonify({'success': False, 'message': 'Invalid language'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/')
def index():
    """Render main desktop page"""
    # Auto-login as admin for SaaS integration
    if 'username' not in session:
        session['username'] = 'admin'
        session['role'] = 'admin'
        session['user_display_name'] = 'Administrator'
        session['language'] = 'ar'
    
    if 'session_key' not in session:
        session['session_key'] = str(uuid.uuid4())
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    if user_id not in chat_sessions:
        chat_sessions[user_id] = []
    
    lang = request.args.get('lang', session.get('language', 'ar'))
    session['language'] = lang
    
    theme = get_current_theme()
    theme_settings = load_theme_settings()
    user_role = session.get('role', 'user')
    
    return render_template('desktop.html', lang=lang, theme=theme, theme_settings=theme_settings, user_role=user_role, timestamp=int(datetime.now().timestamp()))

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        current_session_id = data.get('current_session_id')
        
        if not message:
            lang = session.get('language', 'ar')
            error_msg = 'الرجاء إدخال رسالة' if lang == 'ar' else 'Please enter a message'
            return jsonify({'error': error_msg}), 400
        
        session_key = session.get('session_key', str(uuid.uuid4()))
        session['session_key'] = session_key
        user_id = session.get('user_id')
        
        response = ""
        for chunk in chat_agent.generate_response(message, session_key):
            if chunk:
                # Since its the chat endpoint not the stream-chat!
                response += chunk
        
        if user_id:
            if current_session_id:
                for chat_session in chat_sessions.get(user_id, []):
                    if chat_session['id'] == current_session_id:
                        chat_session['messages'].append({
                            'user': message,
                            'bot': response,
                            'timestamp': datetime.now().isoformat()
                        })
                        chat_session['updated_at'] = datetime.now().isoformat()
                        chat_session['title'] = message[:50] + ('...' if len(message) > 50 else '')
                        break
            else:
                new_session = {
                    'id': str(uuid.uuid4()),
                    'title': message[:50] + ('...' if len(message) > 50 else ''),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'messages': [{
                        'user': message,
                        'bot': response,
                        'timestamp': datetime.now().isoformat()
                    }]
                }
                if user_id not in chat_sessions:
                    chat_sessions[user_id] = []
                chat_sessions[user_id].insert(0, new_session)
                current_session_id = new_session['id']
        
        return jsonify({
            'response': response,
            'session_key': session_key,
            'current_session_id': current_session_id
        })
    
    except Exception as e:
        lang = session.get('language', 'ar')
        error_msg = f'حدث خطأ: {str(e)}' if lang == 'ar' else f'Error: {str(e)}'
        return jsonify({'error': error_msg}), 500

@app.route('/stream-chat', methods=['POST', 'GET'])
def stream_chat():
    """Handle streaming chat messages"""
    try:
        from flask import Response, stream_with_context
        
        # Support both POST and GET (for EventSource)
        if request.method == 'GET':
            message = request.args.get('message', '')
            current_session_id = request.args.get('current_session_id')
        else:
            data = request.get_json()
            message = data.get('message', '')
            current_session_id = data.get('current_session_id')
        
        if not message:
            lang = session.get('language', 'ar')
            error_msg = 'الرجاء إدخال رسالة' if lang == 'ar' else 'Please enter a message'
            return jsonify({'error': error_msg}), 400
        
        session_key = session.get('session_key', str(uuid.uuid4()))
        session['session_key'] = session_key
        user_id = session.get('user_id')
        
        full_response = []
        
        def generate():
            for chunk in chat_agent.generate_response(message, session_key):
                if chunk:
                    full_response.append(chunk)
                    yield f"data: {chunk}\n\n"
            
            # Save to chat history after streaming completes
            if user_id:
                complete_response = ''.join(full_response)
                if current_session_id:
                    for chat_session in chat_sessions.get(user_id, []):
                        if chat_session['id'] == current_session_id:
                            chat_session['messages'].append({
                                'user': message,
                                'bot': complete_response,
                                'timestamp': datetime.now().isoformat()
                            })
                            chat_session['updated_at'] = datetime.now().isoformat()
                            chat_session['title'] = message[:50] + ('...' if len(message) > 50 else '')
                            break
                else:
                    new_session = {
                        'id': str(uuid.uuid4()),
                        'title': message[:50] + ('...' if len(message) > 50 else ''),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'messages': [{
                            'user': message,
                            'bot': complete_response,
                            'timestamp': datetime.now().isoformat()
                        }]
                    }
                    if user_id not in chat_sessions:
                        chat_sessions[user_id] = []
                    chat_sessions[user_id].insert(0, new_session)
            
            yield "event: end\ndata: complete\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        lang = session.get('language', 'ar')
        error_msg = f'حدث خطأ: {str(e)}' if lang == 'ar' else f'Error: {str(e)}'
        return jsonify({'error': error_msg}), 500

@app.route('/new-session', methods=['POST'])
def new_session():
    """Create new chat session"""
    session['session_key'] = str(uuid.uuid4())
    return jsonify({
        'session_key': session['session_key'],
        'session_id': None
    })

@app.route('/get-history', methods=['GET'])
def get_history():
    """Get all chat sessions for current user"""
    user_id = session.get('user_id')
    if not user_id or user_id not in chat_sessions:
        return jsonify({'sessions': []})
    
    sessions_summary = []
    for chat_session in chat_sessions[user_id]:
        sessions_summary.append({
            'id': chat_session['id'],
            'title': chat_session['title'],
            'created_at': chat_session['created_at'],
            'updated_at': chat_session['updated_at'],
            'message_count': len(chat_session['messages'])
        })
    
    return jsonify({'sessions': sessions_summary})

@app.route('/get-session/<session_id>', methods=['GET'])
@app.route('/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get full session data"""
    user_id = session.get('user_id')
    if not user_id or user_id not in chat_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    for chat_session in chat_sessions[user_id]:
        if chat_session['id'] == session_id:
            return jsonify({'session': chat_session})
    
    return jsonify({'error': 'Session not found'}), 404

@app.route('/delete-session/<session_id>', methods=['DELETE'])
@app.route('/delete-session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    user_id = session.get('user_id')
    if not user_id or user_id not in chat_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    for i, chat_session in enumerate(chat_sessions[user_id]):
        if chat_session['id'] == session_id:
            chat_sessions[user_id].pop(i)
            return jsonify({'success': True, 'message': 'Session deleted'})
    
    return jsonify({'error': 'Session not found'}), 404

@app.route('/clear-all-history', methods=['POST'])
@app.route('/clear-history', methods=['POST'])
def clear_all_history():
    """Clear all chat history for current user"""
    user_id = session.get('user_id')
    if user_id and user_id in chat_sessions:
        chat_sessions[user_id] = []
    
    return jsonify({'success': True, 'message': 'All history cleared'})

@app.route('/change-theme', methods=['POST'])
@admin_required
def change_theme():
    """Change app theme"""
    try:
        data = request.get_json()
        theme = data.get('theme', 'nhc')
        
        if theme not in ['nhc', 'readpo']:
            return jsonify({'error': 'Invalid theme'}), 400
        
        save_theme_to_env(theme)
        return jsonify({'success': True, 'theme': theme})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-theme', methods=['GET'])
def get_theme():
    """Get current theme"""
    theme = get_current_theme()
    return jsonify({'theme': theme})

@app.route('/change-language/<lang>', methods=['POST'])
def change_language(lang):
    """Change interface language"""
    if lang in ['ar', 'en']:
        session['language'] = lang
        return jsonify({'success': True, 'language': lang})
    return jsonify({'error': 'Invalid language'}), 400

@app.route('/get-settings', methods=['GET'])
@admin_required
def get_settings():
    """Get current settings"""
    current_settings = load_settings_from_env()
    api_key = current_settings.get('api_key', '')
    masked_key = api_key[:7] + '...' if len(api_key) > 7 else ''
    
    safe_settings = current_settings.copy()
    safe_settings['api_key'] = masked_key
    
    return jsonify(safe_settings)

@app.route('/save-settings', methods=['POST'])
@admin_required
def save_settings():
    """Save settings"""
    try:
        data = request.get_json()
        save_settings_to_env(data)
        chat_agent.update_config(data)
        return jsonify({'success': True, 'message': 'تم حفظ الإعدادات بنجاح'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-api-key', methods=['POST'])
@admin_required
def test_api_key():
    """Test API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        provider = data.get('provider')
        
        if not api_key:
            return jsonify({'success': False, 'message': 'الرجاء إدخال مفتاح API'})
            
        # TODO: Implement actual API key testing logic here
        return jsonify({'success': True, 'message': 'المفتاح صالح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Admin Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Render admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    """Render user management page"""
    return render_template('admin_users.html')

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    users = load_users()
    users_list = []
    for username, data in users.items():
        users_list.append({
            'username': username,
            'name': data['name'],
            'role': data['role']
        })
    return jsonify(users_list)

@app.route('/api/users', methods=['POST'])
@admin_required
def add_user():
    """Add new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'user')
        
        if not all([username, password, name]):
            return jsonify({'error': 'جميع الحقول مطلوبة'}), 400
            
        users = load_users()
        if username in users:
            return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400
            
        users[username] = {
            'password': password,
            'name': name,
            'role': role
        }
        save_users(users)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>', methods=['PUT'])
@admin_required
def update_user(username):
    """Update user"""
    try:
        data = request.get_json()
        users = load_users()
        
        if username not in users:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
            
        if 'password' in data and data['password']:
            users[username]['password'] = data['password']
        if 'name' in data:
            users[username]['name'] = data['name']
        if 'role' in data:
            users[username]['role'] = data['role']
            
        save_users(users)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>', methods=['DELETE'])
@admin_required
def delete_user(username):
    """Delete user"""
    try:
        if username == 'admin':
            return jsonify({'error': 'لا يمكن حذف المدير الرئيسي'}), 400
            
        users = load_users()
        if username in users:
            del users[username]
            save_users(users)
            return jsonify({'success': True})
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/theme')
@admin_required
def admin_theme():
    """Render theme customization page"""
    return render_template('admin_theme.html', timestamp=int(datetime.now().timestamp()))

@app.route('/api/theme/settings', methods=['GET'])
def get_theme_settings():
    """Get theme settings"""
    return jsonify(load_theme_settings())

@app.route('/api/theme/settings', methods=['POST'])
@admin_required
def update_theme_settings():
    """Update theme settings"""
    try:
        data = request.get_json()
        save_theme_settings(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/theme/reset', methods=['POST'])
@admin_required
def reset_theme():
    """Reset theme to default"""
    try:
        if os.path.exists('theme.json'):
            os.remove('theme.json')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/theme/logo', methods=['POST'])
@admin_required
def upload_logo():
    """Upload logo image"""
    try:
        if 'logo' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['logo']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file:
            filename = secrets.token_hex(8) + '_' + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Update theme settings
            theme = load_theme_settings()
            theme['logo']['type'] = 'image'
            theme['logo']['url'] = f"/static/uploads/{filename}"
            save_theme_settings(theme)
            
            return jsonify({'success': True, 'url': theme['logo']['url']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/theme/background', methods=['POST'])
@admin_required
def upload_background():
    """Upload background image"""
    try:
        if 'background' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['background']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file:
            filename = secrets.token_hex(8) + '_' + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Update theme settings
            theme = load_theme_settings()
            theme['background_image'] = f"/static/uploads/{filename}"
            save_theme_settings(theme)
            
            return jsonify({'success': True, 'url': theme['background_image']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def hex_to_rgba(hex_color, opacity=1.0):
    """Convert hex color to rgba"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})'
    except:
        return hex_color

@app.route('/custom-theme.css')
def custom_theme_css():
    theme = load_theme_settings()
    colors = theme.get('colors', {})
    opacity = theme.get('opacity', {})
    font = theme.get('font', 'Cairo')
    background_image = theme.get('background_image', '')
    
    # Get opacity values (convert from 0-100 to 0-1)
    # Note: 0% = no transparency (solid), 100% = full transparency
    sidebar_opacity = 1 - (opacity.get('sidebar', 0) / 100)
    background_opacity = 1 - (opacity.get('background', 0) / 100)
    widget_opacity = 1 - (opacity.get('widget', 0) / 100)
    chat_msg_opacity = 1 - (opacity.get('chat_msg', 0) / 100)
    
    # Get background color and create rgba version for glass effect
    bg_color = colors.get('background', '#F5F7FA')
    sidebar_color = colors.get('sidebar', '#FAFBFC')
    
    css = f"""
    :root {{
        /* Primary Colors */
        --primary: {colors.get('primary', '#00A651')};
        --primary-dark: {colors.get('primary_dark', '#008542')};
        --primary-light: {colors.get('primary_light', '#E8F5E9')};
        --secondary: {colors.get('secondary', '#1E88E5')};
        
        /* Legacy support */
        --nhc-green: {colors.get('primary', '#00A651')};
        --nhc-dark-green: {colors.get('primary_dark', '#008542')};
        --nhc-light-green: {colors.get('primary_light', '#E8F5E9')};
        --nhc-blue: {colors.get('secondary', '#1E88E5')};
        
        /* Background Colors */
        --color-background: {bg_color};
        --bg-color: {bg_color};
        --glass-bg: {hex_to_rgba(bg_color, background_opacity)};
        
        /* Sidebar */
        --color-sidebar: {hex_to_rgba(sidebar_color, sidebar_opacity)};
        --color-sidebar-text: {colors.get('sidebar_text', '#1A1D1F')};
        
        /* Text Colors */
        --color-text-primary: {colors.get('text_primary', '#1A1D1F')};
        --color-text-secondary: {colors.get('text_secondary', '#6F7782')};
        --text-primary: {colors.get('text_primary', '#1A1D1F')};
        --text-secondary: {colors.get('text_secondary', '#6F7782')};
        
        /* Message Colors */
        --user-message-bg: {hex_to_rgba(colors.get('user_msg_bg', '#F0F4F8'), chat_msg_opacity)};
        --bot-message-bg: {hex_to_rgba(colors.get('bot_msg_bg', '#FFFFFF'), chat_msg_opacity)};
        --ai-badge-bg: {colors.get('ai_badge_bg', '#00A651')};
        
        /* App Title Color */
        --app-title-color: {colors.get('app_title_color', '#FFFFFF')};
        
        /* Taskbar Icons Color */
        --taskbar-icons-color: {colors.get('taskbar_icons_color', '#FFFFFF')};
        
        /* Widget Colors */
        --header-bar-bg-color: {hex_to_rgba(colors.get('header_bar_bg_color', '#19192D'), widget_opacity)};
        --widget-bg-color: {hex_to_rgba(colors.get('widget_bg_color', '#1E1E32'), widget_opacity)};
        --widget-border-color: {colors.get('widget_border_color', '#FFFFFF')};
        --widget-title-color: {colors.get('widget_title_color', '#FFFFFF')};
        --widget-text-color: {colors.get('widget_text_color', '#CCCCCC')};
        --widget-icon-ai: {colors.get('widget_icon_ai', '#667EEA')};
        --widget-icon-chat: {colors.get('widget_icon_chat', '#0078D4')};
        --widget-icon-system: {colors.get('widget_icon_system', '#00A651')};
        --widget-icon-actions: {colors.get('widget_icon_actions', '#FF6B6B')};
        
        /* Opacity values */
        --sidebar-opacity: {sidebar_opacity};
        --background-opacity: {background_opacity};
        --widget-opacity: {widget_opacity};
        --chat-msg-opacity: {chat_msg_opacity};
        
        /* Font */
        --font-primary: '{font}', sans-serif;
    }}
    
    body {{
        font-family: var(--font-primary) !important;
    }}
    
    /* App Title Styling */
    .app-title {{
        color: {colors.get('app_title_color', '#FFFFFF')} !important;
        background: linear-gradient(135deg, {colors.get('app_title_color', '#FFFFFF')} 0%, {hex_to_rgba(colors.get('app_title_color', '#FFFFFF'), 0.7)} 50%, {colors.get('app_title_color', '#FFFFFF')} 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }}
    
    /* Desktop Background */
    .desktop-background {{
        background: linear-gradient(135deg, {colors.get('primary', '#00A651')}40, {colors.get('secondary', '#1E88E5')}40) !important;
    }}
    
    .desktop-background .bg-image {{
        opacity: 1;
    }}
    
    /* Windows Glass Effect - More Transparent */
    .app-window {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
        backdrop-filter: blur(calc((1 - {background_opacity}) * 40px)) saturate(180%) !important;
        -webkit-backdrop-filter: blur(calc((1 - {background_opacity}) * 40px)) saturate(180%) !important;
    }}
    
    /* Chat Sidebar - Glass Effect */
    .chat-sidebar {{
        background: {hex_to_rgba(sidebar_color, sidebar_opacity)} !important;
        backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 20px)) !important;
        -webkit-backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 20px)) !important;
    }}
    
    /* Chat Main Area - Glass Effect */
    .chat-main {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
        backdrop-filter: blur(calc((1 - {background_opacity}) * 10px)) !important;
        -webkit-backdrop-filter: blur(calc((1 - {background_opacity}) * 10px)) !important;
    }}
    
    /* Window Header */
    .window-header {{
        background: {hex_to_rgba(sidebar_color, sidebar_opacity)} !important;
        backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 10px)) !important;
        -webkit-backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 10px)) !important;
    }}
    
    /* Taskbar - Glass Effect */
    .taskbar {{
        background: {hex_to_rgba(bg_color, 0.2)} !important;
        backdrop-filter: blur(50px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(50px) saturate(180%) !important;
    }}
    
    .taskbar-center {{
        background: {hex_to_rgba(sidebar_color, 0.15)} !important;
    }}
    
    /* Taskbar Icons */
    .taskbar-btn {{
        color: {colors.get('taskbar_icons_color', '#FFFFFF')} !important;
    }}
    
    .taskbar-btn:hover {{
        color: {colors.get('taskbar_icons_color', '#FFFFFF')} !important;
    }}
    
    .start-btn svg,
    .taskbar-center .taskbar-btn svg,
    .system-tray svg {{
        color: {colors.get('taskbar_icons_color', '#FFFFFF')} !important;
    }}
    
    .tray-time,
    #taskbarTime,
    #taskbarDate {{
        color: {colors.get('taskbar_icons_color', '#FFFFFF')} !important;
    }}
    
    /* Buttons */
    .new-chat-btn,
    .send-btn {{
        background: linear-gradient(135deg, {colors.get('primary', '#00A651')}, {colors.get('primary_dark', '#008542')}) !important;
    }}
    
    .new-chat-btn:hover,
    .send-btn:hover {{
        box-shadow: 0 5px 20px {colors.get('primary', '#00A651')}60 !important;
    }}
    
    /* Start Menu - Glass Effect */
    .start-menu {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
        backdrop-filter: blur(calc((1 - {background_opacity}) * 50px)) saturate(200%) !important;
        -webkit-backdrop-filter: blur(calc((1 - {background_opacity}) * 50px)) saturate(200%) !important;
    }}
    
    .start-btn:hover {{
        background: {colors.get('primary', '#00A651')} !important;
    }}
    
    /* User Dropdown - Glass Effect */
    .user-dropdown {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
        backdrop-filter: blur(calc((1 - {background_opacity}) * 50px)) saturate(200%) !important;
        -webkit-backdrop-filter: blur(calc((1 - {background_opacity}) * 50px)) saturate(200%) !important;
    }}
    
    /* User Avatar */
    .user-avatar,
    .logo-icon {{
        background: linear-gradient(135deg, {colors.get('primary', '#00A651')}, {colors.get('secondary', '#1E88E5')}) !important;
    }}
    
    /* Active States */
    .taskbar-btn.active::after {{
        background: {colors.get('primary', '#00A651')} !important;
    }}
    
    .lang-btn.active,
    .lang-btn:hover {{
        background: {colors.get('primary', '#00A651')} !important;
        border-color: {colors.get('primary', '#00A651')} !important;
    }}
    
    /* Input Wrapper - Glass Effect */
    .input-wrapper {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
        backdrop-filter: blur(calc((1 - {background_opacity}) * 10px)) !important;
        -webkit-backdrop-filter: blur(calc((1 - {background_opacity}) * 10px)) !important;
    }}
    
    /* Quick Actions - Glass Effect */
    .quick-action {{
        background: {hex_to_rgba(sidebar_color, sidebar_opacity)} !important;
        backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 10px)) !important;
        -webkit-backdrop-filter: blur(calc((1 - {sidebar_opacity}) * 10px)) !important;
    }}
    
    /* Suggestions - Glass Effect */
    .suggestion {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
    }}
    
    /* Header Bar Styling */
    .top-header-bar {{
        background: {hex_to_rgba(colors.get('header_bar_bg_color', '#19192D'), widget_opacity)} !important;
    }}
    
    /* Desktop Widgets Styling */
    .desktop-widget {{
        background: {hex_to_rgba(colors.get('widget_bg_color', '#1E1E32'), widget_opacity)} !important;
        border-color: {hex_to_rgba(colors.get('widget_border_color', '#FFFFFF'), widget_opacity)} !important;
    }}
    
    .widget-title {{
        color: {colors.get('widget_title_color', '#FFFFFF')} !important;
    }}
    
    .widget-body,
    .widget-body * {{
        color: {colors.get('widget_text_color', '#CCCCCC')};
    }}
    
    .stat-value,
    .model-name,
    .action-title {{
        color: {colors.get('widget_title_color', '#FFFFFF')} !important;
    }}
    
    .widget-icon.ai-icon {{
        background: linear-gradient(135deg, {colors.get('widget_icon_ai', '#667EEA')}, {colors.get('widget_icon_ai', '#667EEA')}99) !important;
    }}
    
    .widget-icon.chat-stats-icon {{
        background: linear-gradient(135deg, {colors.get('widget_icon_chat', '#0078D4')}, {colors.get('widget_icon_chat', '#0078D4')}99) !important;
    }}
    
    .widget-icon.system-icon {{
        background: linear-gradient(135deg, {colors.get('widget_icon_system', '#00A651')}, {colors.get('widget_icon_system', '#00A651')}99) !important;
    }}
    
    .widget-icon.actions-icon {{
        background: linear-gradient(135deg, {colors.get('widget_icon_actions', '#FF6B6B')}, {colors.get('widget_icon_actions', '#FF6B6B')}99) !important;
    }}
    
    /* Legacy Main Content */
    .main-content {{
        background: {hex_to_rgba(bg_color, background_opacity)} !important;
    }}
    
    .vr-background {{
        background-image: url('{background_image}') !important;
    }}
    """
    return Response(css, mimetype='text/css')

# ============================================
# Widget Management Functions and Routes
# ============================================

GEMINI_API_KEY = 'AIzaSyAmeEoIeLp-Fkt4cev87gVW3xqvfVELvbo'

def load_widgets():
    """Load widgets from JSON file"""
    if os.path.exists('widgets.json'):
        try:
            with open('widgets.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('widgets', [])
        except:
            return []
    return []

def save_widgets(widgets_list):
    """Save widgets to JSON file"""
    with open('widgets.json', 'w', encoding='utf-8') as f:
        json.dump({'widgets': widgets_list}, f, ensure_ascii=False, indent=4)

@app.route('/admin/widgets')
@admin_required
def admin_widgets():
    """Render widget management page"""
    return render_template('admin_widgets.html')

@app.route('/api/widgets', methods=['GET'])
def get_widgets():
    """Get all widgets - available to all logged in users"""
    widgets = load_widgets()
    return jsonify({'widgets': widgets})

@app.route('/api/widgets', methods=['POST'])
@admin_required
def add_widget():
    """Add new widget"""
    try:
        data = request.get_json()
        widgets = load_widgets()
        
        new_widget = {
            'id': str(uuid.uuid4()),
            'name': data.get('name', 'ودجت جديد'),
            'name_en': data.get('name_en', 'New Widget'),
            'type': data.get('type', 'custom'),
            'icon': data.get('icon', 'custom'),
            'active': data.get('active', True),
            'order': len(widgets) + 1,
            'html_content': data.get('html_content', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        widgets.append(new_widget)
        save_widgets(widgets)
        
        return jsonify({'success': True, 'widget': new_widget})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>', methods=['PUT'])
@admin_required
def update_widget(widget_id):
    """Update widget"""
    try:
        data = request.get_json()
        widgets = load_widgets()
        
        for i, widget in enumerate(widgets):
            if widget['id'] == widget_id:
                widgets[i]['name'] = data.get('name', widget['name'])
                widgets[i]['name_en'] = data.get('name_en', widget.get('name_en', ''))
                widgets[i]['type'] = data.get('type', widget.get('type', 'custom'))
                widgets[i]['icon'] = data.get('icon', widget.get('icon', 'custom'))
                widgets[i]['html_content'] = data.get('html_content', widget.get('html_content', ''))
                widgets[i]['active'] = data.get('active', widget.get('active', True))
                widgets[i]['updated_at'] = datetime.now().isoformat()
                
                save_widgets(widgets)
                return jsonify({'success': True, 'widget': widgets[i]})
        
        return jsonify({'success': False, 'error': 'Widget not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>/toggle', methods=['PUT'])
@admin_required
def toggle_widget(widget_id):
    """Toggle widget active state"""
    try:
        data = request.get_json()
        widgets = load_widgets()
        
        for i, widget in enumerate(widgets):
            if widget['id'] == widget_id:
                widgets[i]['active'] = data.get('active', not widget.get('active', True))
                widgets[i]['updated_at'] = datetime.now().isoformat()
                
                save_widgets(widgets)
                return jsonify({'success': True, 'active': widgets[i]['active']})
        
        return jsonify({'success': False, 'error': 'Widget not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>', methods=['DELETE'])
@admin_required
def delete_widget(widget_id):
    """Delete widget"""
    try:
        widgets = load_widgets()
        
        for i, widget in enumerate(widgets):
            if widget['id'] == widget_id:
                widgets.pop(i)
                save_widgets(widgets)
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Widget not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/generate', methods=['POST'])
@admin_required
def generate_widget():
    """Generate widget HTML using Gemini AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'يرجى إدخال وصف للودجت'})
        
        # Prepare the prompt for Gemini
        system_prompt = """أنت مصمم ودجات محترف. مهمتك إنشاء كود HTML للودجات بناءً على وصف المستخدم.

قواعد مهمة:
1. أنشئ فقط المحتوى الداخلي للودجت (بدون wrapper div)
2. استخدم التنسيق والألوان المتناسقة
3. استخدم الأيقونات SVG عند الحاجة
4. اجعل التصميم متجاوب وأنيق
5. استخدم الـ CSS inline أو classes بسيطة
6. الخطوط العربية مدعومة (Cairo)
7. أرجع فقط كود HTML بدون شرح إضافي
8. لا تستخدم أي JavaScript
9. استخدم ألوان متناسقة مثل: #00A651 (أخضر), #1E88E5 (أزرق), #667EEA (بنفسجي)
10. اجعل العناصر صغيرة ومناسبة للودجت

مثال على الإخراج:
<div style="display: flex; flex-direction: column; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: rgba(0,166,81,0.1); border-radius: 10px;">
        <span style="font-size: 24px;">📊</span>
        <div>
            <div style="font-weight: 600; color: #1A1D1F;">العنوان</div>
            <div style="font-size: 0.85rem; color: #6F7782;">الوصف</div>
        </div>
    </div>
</div>"""

        full_prompt = f"{system_prompt}\n\nوصف الودجت المطلوب:\n{prompt}"
        
        # Call Gemini API
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        gemini_payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(gemini_url, json=gemini_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text
            generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Clean up the response - extract HTML
            html_content = generated_text.strip()
            
            # Remove markdown code blocks if present
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].split('```')[0].strip()
            
            # Generate a suggested name from the prompt
            suggested_name = prompt[:30] + ('...' if len(prompt) > 30 else '')
            
            return jsonify({
                'success': True,
                'html': html_content,
                'suggested_name': suggested_name,
                'message': 'تم إنشاء الودجت بنجاح! ✨ يمكنك معاينته أدناه وتعديله إذا أردت.'
            })
        elif response.status_code == 429:
            # Rate limit - use fallback template
            return generate_fallback_widget(prompt)
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'خطأ في API')
            
            # Check if it's a quota/rate limit error
            if 'exhausted' in error_msg.lower() or 'quota' in error_msg.lower() or '429' in str(response.status_code):
                return generate_fallback_widget(prompt)
            
            return jsonify({'success': False, 'error': f'خطأ من Gemini: {error_msg}'})
            
    except requests.Timeout:
        return jsonify({'success': False, 'error': 'انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى.'})
    except Exception as e:
        # On any error, try fallback
        return generate_fallback_widget(prompt)

def generate_fallback_widget(prompt):
    """Generate a simple widget template when AI is unavailable"""
    # Simple keyword-based template selection
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['إحصائ', 'stats', 'أرقام', 'عدد', 'count']):
        html = '''<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
    <div style="padding: 15px; background: rgba(0,166,81,0.1); border-radius: 12px; text-align: center;">
        <div style="font-size: 1.8rem; font-weight: 700; color: #00A651;">150</div>
        <div style="font-size: 0.85rem; color: #6F7782;">إجمالي</div>
    </div>
    <div style="padding: 15px; background: rgba(30,136,229,0.1); border-radius: 12px; text-align: center;">
        <div style="font-size: 1.8rem; font-weight: 700; color: #1E88E5;">25</div>
        <div style="font-size: 0.85rem; color: #6F7782;">اليوم</div>
    </div>
    <div style="padding: 15px; background: rgba(102,126,234,0.1); border-radius: 12px; text-align: center;">
        <div style="font-size: 1.8rem; font-weight: 700; color: #667EEA;">89%</div>
        <div style="font-size: 0.85rem; color: #6F7782;">نسبة النجاح</div>
    </div>
    <div style="padding: 15px; background: rgba(255,107,107,0.1); border-radius: 12px; text-align: center;">
        <div style="font-size: 1.8rem; font-weight: 700; color: #FF6B6B;">1.2s</div>
        <div style="font-size: 0.85rem; color: #6F7782;">متوسط الوقت</div>
    </div>
</div>'''
    elif any(word in prompt_lower for word in ['قائمة', 'list', 'عناصر', 'items']):
        html = '''<div style="display: flex; flex-direction: column; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(0,166,81,0.1); border-radius: 10px;">
        <span style="font-size: 20px;">✅</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #1A1D1F;">العنصر الأول</div>
            <div style="font-size: 0.8rem; color: #6F7782;">وصف قصير</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(30,136,229,0.1); border-radius: 10px;">
        <span style="font-size: 20px;">📌</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #1A1D1F;">العنصر الثاني</div>
            <div style="font-size: 0.8rem; color: #6F7782;">وصف قصير</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(102,126,234,0.1); border-radius: 10px;">
        <span style="font-size: 20px;">⭐</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #1A1D1F;">العنصر الثالث</div>
            <div style="font-size: 0.8rem; color: #6F7782;">وصف قصير</div>
        </div>
    </div>
</div>'''
    elif any(word in prompt_lower for word in ['تقدم', 'progress', 'نسبة', 'percentage']):
        html = '''<div style="display: flex; flex-direction: column; gap: 15px;">
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-weight: 500; color: #1A1D1F;">المهام المكتملة</span>
            <span style="color: #00A651; font-weight: 600;">75%</span>
        </div>
        <div style="height: 8px; background: rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
            <div style="width: 75%; height: 100%; background: linear-gradient(90deg, #00A651, #00D68F); border-radius: 10px;"></div>
        </div>
    </div>
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-weight: 500; color: #1A1D1F;">استخدام الموارد</span>
            <span style="color: #1E88E5; font-weight: 600;">45%</span>
        </div>
        <div style="height: 8px; background: rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
            <div style="width: 45%; height: 100%; background: linear-gradient(90deg, #1E88E5, #00BCF2); border-radius: 10px;"></div>
        </div>
    </div>
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-weight: 500; color: #1A1D1F;">الأداء العام</span>
            <span style="color: #667EEA; font-weight: 600;">92%</span>
        </div>
        <div style="height: 8px; background: rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
            <div style="width: 92%; height: 100%; background: linear-gradient(90deg, #667EEA, #764BA2); border-radius: 10px;"></div>
        </div>
    </div>
</div>'''
    else:
        # Default info widget
        html = f'''<div style="display: flex; flex-direction: column; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 12px; padding: 15px; background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border-radius: 12px; border: 1px solid rgba(102,126,234,0.2);">
        <div style="width: 45px; height: 45px; background: linear-gradient(135deg, #667EEA, #764BA2); border-radius: 10px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 22px;">✨</span>
        </div>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #1A1D1F; font-size: 1rem;">ودجت مخصص</div>
            <div style="font-size: 0.85rem; color: #6F7782; margin-top: 2px;">{prompt[:50]}...</div>
        </div>
    </div>
    <div style="padding: 12px; background: rgba(0,166,81,0.08); border-radius: 10px; text-align: center;">
        <div style="font-size: 0.9rem; color: #6F7782;">يمكنك تعديل هذا المحتوى حسب احتياجاتك</div>
    </div>
</div>'''
    
    suggested_name = prompt[:30] + ('...' if len(prompt) > 30 else '')
    
    return jsonify({
        'success': True,
        'html': html,
        'suggested_name': suggested_name,
        'message': '⚠️ تم إنشاء قالب أساسي (API مشغول حالياً). يمكنك تعديله يدوياً أو المحاولة مرة أخرى لاحقاً.'
    })

@app.route('/api/widgets/active', methods=['GET'])
def get_active_widgets():
    """Get active widgets for desktop display"""
    widgets = load_widgets()
    active_widgets = [w for w in widgets if w.get('active', False)]
    return jsonify({'widgets': active_widgets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

