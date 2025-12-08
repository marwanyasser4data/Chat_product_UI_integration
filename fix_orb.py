import re

file_path = 'templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the welcome message content
pattern = r'<div class="ai-badge">AI</div>.*?</p>'
replacement = '''<div class="orb-container">
                        <div class="orb"></div>
                        <div class="orb-glow"></div>
                    </div>'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Replacement complete!')
