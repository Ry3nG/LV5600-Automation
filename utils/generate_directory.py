import os

def generate_directory_structure(directory, indent=''):
    tree = ''
    items = os.listdir(directory)
    items.sort()  # Sort the items alphabetically

    for item in items:
        path = os.path.join(directory, item)
        if os.path.isfile(path):
            tree += f'{indent}├── {item}\n'
        elif os.path.isdir(path):
            tree += f'{indent}├── {item}\n'
            tree += generate_directory_structure(path, indent + '│   ')
    
    return tree

# Specify the root directory of your project
root_directory = 'E:\\M15\\Leader LV5600 PoC\\LV5600-Automation'

# Generate the directory structure
directory_structure = generate_directory_structure(root_directory)

# Print or save the directory structure as markdown
print(directory_structure)
