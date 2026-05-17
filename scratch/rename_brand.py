import os

# We will recursively scan all project files (.html, .py) and replace 'Azhar-foodExp' with 'Azhar-foodExp'
files_to_update = []
for root, dirs, files in os.walk('.'):
    # Skip temporary, environment, or build directories
    if any(ignore in root for ignore in ['venv', '.git', '.vercel', '__pycache__', 'node_modules']):
        continue
    for file in files:
        if file.endswith(('.html', '.py', '.css')):
            files_to_update.append(os.path.join(root, file))

print(f"Found {len(files_to_update)} files to process.")

updated_count = 0
for filepath in files_to_update:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for any variation of Azhar-foodExp
        if 'Azhar-foodExp' in content or 'Azhar-foodExp' in content:
            new_content = content.replace('Azhar-foodExp', 'Azhar-foodExp')
            new_content = new_content.replace('Azhar-foodExp', 'Azhar-foodExp')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated brand in: {filepath}")
            updated_count += 1
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")

print(f"Successfully processed all files. Brand renamed in {updated_count} files!")
