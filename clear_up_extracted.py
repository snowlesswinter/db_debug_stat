import os
import os.path
import shutil

def remove_file(root, file_name):
    file_path = root + "\\" + file_name
    try:
        os.remove(file_path)
        print("reomved file: " + file_path)
    except:
        print("failed to remove file: " + file_path)
      
root = input("directory name:")
for root, dirs, files in os.walk(root):
    for f in files:
        if (os.path.splitext(f)[1] != '.zip'):
            remove_file(root, f)
