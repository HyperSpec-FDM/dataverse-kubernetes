import os

def find_uuid_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == ".uuid":
                file_path = os.path.join(dirpath, filename)
                print("Found .uuid file:", file_path)
                #os.remove(file_path)

# Specify the root directory from which to start searching
root_directory = "."

find_uuid_files(root_directory)