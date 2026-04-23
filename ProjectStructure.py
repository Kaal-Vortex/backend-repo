import os

def generate_tree(startpath, output_file, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.idea', '.vscode'}

    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(startpath):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Calculate depth for indentation
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            
            # Write the directory name
            folder_name = os.path.basename(root)
            if folder_name == os.path.basename(startpath):
                f.write(f"{folder_name}/\n")
            else:
                f.write(f"{indent}├── {folder_name}/\n")
            
            # Write the files in that directory
            sub_indent = ' ' * 4 * (level + 1)
            for i, filename in enumerate(files):
                if i == len(files) - 1 and len(dirs) == 0:
                    f.write(f"{sub_indent}└── {filename}\n")
                else:
                    f.write(f"{sub_indent}├── {filename}\n")

if __name__ == "__main__":
    # Path to the downloaded repo
    project_directory = "D:\Desktop\Online Savaari\onlinesavaari-back-test-test"  # Change this to your repo path if not running inside it
    output_filename = "project_structure.txt"
    
    generate_tree(project_directory, output_filename)
    print(f"Success! Structure saved to {output_filename}")