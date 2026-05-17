import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

# Patterns to remove (including the parent div)
patterns = [
    r'<div class="contact-item">\s*<i class="fas fa-location-dot"></i>\s*<p class="contact-text">LPU Campus, Phagwara, Punjab</p>\s*</div>',
    r'<div class="contact-item">\s*<i class="fas fa-shield-check"></i>\s*<p class="contact-text">Secure & Trusted Platform</p>\s*</div>',
    # Variations with different icons or tags
    r'<div class="contact-item">\s*<i class="fas fa-map-marker-alt"></i>\s*<p class="contact-text">LPU Campus, Phagwara, Punjab</p>\s*</div>',
    r'<div class="contact-item">\s*<i class="fas fa-shield-alt"></i>\s*<p class="contact-text">Secure & Trusted Platform</p>\s*</div>'
]

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.startswith('admin_') and file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for pattern in patterns:
                new_content = re.sub(pattern, '', new_content, flags=re.DOTALL)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {file}")
