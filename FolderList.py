import os
import json

def get_folder_structure(directory, exclude_folders=None):
    """
    Recursively builds the folder structure of the given directory, 
    excluding specified folders.
    """
    if exclude_folders is None:
        exclude_folders = []

    folder_structure = {}
    try:
        for item in os.listdir(directory):  # List all items in the directory
            item_path = os.path.join(directory, item)  # Full path of the item
            if os.path.isdir(item_path):  # If it's a folder
                if item in exclude_folders:
                    continue  # Skip excluded folders
                folder_structure[item] = get_folder_structure(item_path, exclude_folders)
            else:
                folder_structure[item] = "file"  # Mark as file
    except PermissionError:  # Handle cases where the directory can't be accessed
        folder_structure = "Permission Denied"
    return folder_structure

# Replace 'project_folder' with the folder you want to scan
project_folder = "C:/Users/Taroneez/Desktop/recommendation system"  # Adjust this path
excluded_folders = ["venv", ".git"]  # Folders to exclude

folder_structure = get_folder_structure(project_folder, exclude_folders=excluded_folders)

# Print the structure as a formatted JSON string
print(json.dumps(folder_structure, indent=2))
