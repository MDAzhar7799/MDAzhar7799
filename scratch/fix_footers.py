import os
import re

templates_dir = r'c:\Users\MD AZHAR\Desktop\lawgate & lpu online food\lpu-food python\templates'

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace variants
            new_content = content.replace('Made with ♥', 'Made')
            new_content = new_content.replace('Made with <span>❤</span>', 'Made')
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {file}")
