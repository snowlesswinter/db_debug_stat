import os
import os.path
import zipfile
import shutil

files_found = []

def explore_file(log_file_name, hash):     
    try:
        log_file = open(log_file_name, 'r')
        for line in log_file.readlines():
            if (line.find('ServerMusicID') != -1):
                return true

        log_file.close()
        return false
    except:
        print('FAILED to explore: ' + log_file_name)
        return false

def unzip(zip_file_path):
    try:
        zip_file = zipfile.ZipFile(zip_file_path, 'r')
        content_files = zip_file.namelist()
        for file_name in content_files:
            if os.path.splitext(file_name)[1] == '.dblog':
                zipfile.extract(zip_dir, file_name)
                return zip_dir + '\\' + file_name

        return '' # no debug log files found in the zip file
    except:
        if (os.path.getsize(zip_file_path) == 0):
            print('empty file')
        else:
            print("FAILED to extract: " + zip_dir + '\\' + zip_file_name)

        return ''

def explore(zip_dir, zip_file_name):
    try:
        zip_file_path = zip_dir + '\\' + zip_file_name
        log_file_path = unzip(zip_file_path)
        if len(log_file_path) == 0:
            return

        if explore_file(log_file_path):
            files_found.append(zip_file_name)
        
        try:
            os.remove(log_file_path)
        except:
            pass
    except:
        print('FAILED to analyze: ' + zip_dir + '\\' + zip_file_name)
      
root = input('directory name:')
for root, dirs, files in os.walk(root):
    for f in files:
        if os.path.splitext(f)[1] == '.zip':
            print('begin to explore: ' + root + '\\' + f)
            explore(root, f)
            print('exploration done')

print('files found:')
for file in files_found:
    print('\t' + file)
