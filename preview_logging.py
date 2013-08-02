import inspect
import os
import os.path
import shutil
import zipfile

def get_current_path():
    my_path = inspect.getfile(inspect.currentframe())
    my_relative_path = os.path.split(my_path)[0]
    my_abs_path = os.path.abspath(my_relative_path)

    # realpath() with make your script run, even if you symlink it :)
    return os.path.realpath(my_abs_path)

def main():
    version = input('version:')
    root = get_current_path()
    print_usage()
    while True:
        command = input('Input command:')
        if command == 'exit':
            break
        elif command.find('u ') == 0 or command.find('user_id ') == 0:
            user_id = command[command.find(' ') + 1:]
            if not walk_through_and_analyze(root, user_id, version):
                print('LOG NOT FOUND:', user_id)
                
        else:
            print_usage()

def print_usage():
    print('Usage:')
    print('exit:\t\t\tExit the program.')
    print('user_id,u [user id]:\tDump the specified log.')

def render(log_file_path_name, zip_file_name):
    try:
        print('start to dump file: ', zip_file_name)
        log_file = open(log_file_path_name, 'r')
        for line in log_file.readlines():
            print(line, end='')

        print('')
        log_file.close()
    except:
        print('FAILED to render: ' + log_file_name)

def unzip_and_render(zip_dir, zip_file_name):
    try:
        zip_file_path = zip_dir + '\\' + zip_file_name
        content_files = []
        log_file_name = ''
        
        # unzip all debug log files
        try:
            zip_file = zipfile.ZipFile(zip_file_path, 'r')
            content_files = zip_file.namelist()
            for file_name in content_files:
                if os.path.splitext(file_name)[1] == '.old':
                    zip_file.extract(file_name, zip_dir)
                    log_file_name = file_name
                    break
        except:
            if os.path.getsize(zip_file_path) == 0:
                print('empty file')
            else:
                print("FAILED to extract: " + zip_dir + '\\' + zip_file_name)

            return

        log_file_path_name = zip_dir + '\\' + log_file_name
        render(log_file_path_name, os.path.splitext(zip_file_name)[0])
        try:
            os.remove(log_file_path_name)
        except:
            pass
        
    except:
        print('FAILED to render: ' + zip_dir + '\\' + zip_file_name)

def walk_through_and_analyze(start_from, user_id, version):
    found = False
    for root, dirs, files in os.walk(start_from + '\\' + version):
        for file in files:
            if os.path.splitext(file)[1] == '.zip' and file.find(user_id) != -1:
                unzip_and_render(root, file)
                found = True

    return found

# go
main()
