import os
import os.path
import zipfile
import shutil
import traceback

def analyze(global_log, content_files, log_file_name, date, metas_in_text):
    result = 'insert into ' + to_be_imported_name() + ' values ('
    
    metas = metas_in_text.split('.')
    user_id = metas[0]
    svn = metas[1]
    version = metas[2]

    # NOTE: the date in the log file name may not be always correct
    issue_date = format_date(metas[3])
    upload_date = format_date(date)
    time = format_time(metas[4])
    result += user_id + ',' + svn + ',' + version + ',' + \
              issue_date + ' ' + time + ',' + upload_date

    try:
        log_file = object
        log_file_lines = []
        log_exists = True

        # some zip files may not contain a log file
        try:
            log_file = open(log_file_name, 'r')
        except:
            log_exists = False

        if log_exists:
            log_file_lines = log_file.readlines()

        # basic
        basic = analyze_basic(log_file_lines)
        result += ',' + basic

        # components
        components = analyze_components(content_files)
        result += ',' + components

        # paterns
        paterns = analyze_paterns(log_file_lines)
        result += ',' + paterns

        result += ')\n'
        global_log.writelines([rectify_result(result)])
        if log_exists:
            log_file.close()
            
    except:
        print('FAILED to analyze: ' + metas_in_text)
        traceback.print_exc()

def analyze_basic(log_file_lines):
    if len(log_file_lines) == 0:
        return 'NULL,NULL'
    
    result = ''
    crash_checked = False
    os_version_checked = False
    crash = -1
    os_version = ''
    for line in log_file_lines:
        if not crash_checked:
            if line.find('KUGOU CRASH!!') != -1:
                crash = 1
                crash_checked = True;

        if not os_version_checked:
            if line.find('OS Version:') != -1:
                os_version = line[12:].split(',')[0]
                os_version_checked = True

    # |crash| only valid when the log file is valid
    if os_version_checked and crash < 0:
        crash = 0

    result += os_version + ','
    result += str(crash)
    return result

def analyze_components(content_files):
    components = []
    for file in content_files:
        splitted = os.path.splitext(file);
        if len(splitted) < 2:
            continue
        elif splitted[1] == '.old':
            components.append('log')
        elif splitted[1] == '.db':
            components.append('db')
        elif splitted[1] == '.bak':
            components.append('bak')
        elif splitted[1] == '.db-journal':
            components.append('db-journal')

    result = ''
    for index, component in enumerate(components):
        if index != 0:
            result += ' ' + component
        else:
            result += component
            
    return result

def analyze_paterns(log_file_lines):
    if len(log_file_lines) == 0:
        return 'empty'
    
    # things are going to be a bit nasty here...
    db_lost = False
    single_open = False
    try:
        process_open_db = [
            '******** OPENING DB ********',
            '******** DB OPENED ********'
        ]
        db_lost_desc = [
            'Get DB file info failed, code: 2',
            'Try to recovery data from backup file.',
            'Get backup file info failed, code: 2',
            'Recovery failed, try to create a new one.',
            'Remove DB file failed, code: 2',
            'Remove backup file failed, code: 2',
            'Try creating a new DB file'
        ]

        if match_db_lost_pattern(log_file_lines[1:], process_open_db,
                                 db_lost_desc):
            db_lost = True
            single_open = True
        elif len(log_file_lines) > 2 and \
             log_file_lines[1].find('KUGOU CRASH!!') != -1:
            single_open = True
            db_lost = match_db_lost_pattern(log_file_lines[2:],
                                            process_open_db, db_lost_desc)
        elif len(log_file_lines) > len(process_open_db) + 1:
            match = True
            if log_file_lines[1].find(process_open_db[0]) == -1 or \
               log_file_lines[2].find(process_open_db[1]) == -1:
                match = False

            if match:
                db_lost = match_db_lost_pattern(log_file_lines[3:],
                                                process_open_db, db_lost_desc)
                
    except:
        pass

    result = 'none'
    if db_lost:
        if single_open:
            result = 'db_lost(single_open)'
        else:
            result = 'db_lost'
    else:
        for line in log_file_lines[1:]:
            if line.find('disk I/O error') != -1:
                result = 'io_error'
                break

    return result

def format_date(date):
    if len(date) < 8:
        return ''

    return date[:4] + '-' + date[4:6] + '-' + date[6:]

def format_time(time):
    if len(time) < 6:
        return ''

    return time[:2] + ':' + time[2:4] + ':' + time[4:]

def main():
    root = input('directory name:')
    to_be_imported = open(root + '\\' + to_be_imported_name() + '.txt', 'w')

    for root, dirs, files in os.walk(root):
        for file in files:
            if os.path.splitext(file)[1] == '.zip':
                # print('unzip: ' + root + '\\' + file)
                unzip_and_analyze(to_be_imported, root, file)
                
    to_be_imported.close()

def match_db_lost_pattern(log_file_lines, process_open_db, db_lost_desc):
    match = False
    if len(log_file_lines) == len(process_open_db) + len(db_lost_desc):
        match = True
        if log_file_lines[0].find(process_open_db[0]) == -1 or \
           log_file_lines[-1].find(process_open_db[1]) == -1:
            match = False

        if match:
            for index, line in enumerate(log_file_lines[1:-1]):
                if line.find(db_lost_desc[index]) == -1:
                    match = False
                    break

    return match

def rectify_result(result):
    parenthesis_pos = result.find('(')
    values = result[parenthesis_pos + 1:-2]
    splitted = values.split(',')

    if len(splitted) != 9:
        raise 'wrong values set'

    rectified = ''
    for index, value in enumerate(splitted):
        if index != 0:
            rectified += ','
            
        if index in [0, 3, 4, 5, 7, 8] and value != 'NULL':
            rectified += '\'' + value + '\''
        else:
            rectified += value

    return result[:parenthesis_pos + 1] + rectified + ')\n'

def to_be_imported_name():
    return 'to_be_imported'

def unzip_and_analyze(global_log, zip_dir, zip_file_name):
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

        # for the convenience to locate the directory of a specified file,
        # we need to store the upload date value
        date = zip_dir.rsplit('\\', 1)[1]

        # start translating
        log_file_path_name = zip_dir + '\\' + log_file_name        
        analyze(global_log, content_files, log_file_path_name, date, os.path.splitext(zip_file_name)[0])
        try:
            os.remove(log_file_path_name)
        except:
            pass
            
    except:
        print('FAILED to pre-analyze: ' + zip_dir + '\\' + zip_file_name)
        traceback.print_exc()

# go
main()
