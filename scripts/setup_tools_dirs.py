import os

def create_tool_dirs():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs = [
        'app/tools',
        'app/tools/browser',
        'app/tools/search',
        'app/tools/llm',
        'app/tools/llm/prompt_templates'
    ]
    
    for dir_path in dirs:
        full_path = os.path.join(base_path, dir_path)
        os.makedirs(full_path, exist_ok=True)
        # Create __init__.py in each directory
        init_file = os.path.join(full_path, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')

if __name__ == '__main__':
    create_tool_dirs()
