#!/usr/bin/env python3

import configparser
import logging
import os
import sys

import dropbox
from dropbox.exceptions import ApiError, AuthError, BadInputError
from dropbox.files import WriteMode

logging.basicConfig(format='dbak %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

DBX = False
BACKUP_PATHS = []


def validate_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # check dropbox connection
    try:
        access_token = config['DEFAULT']['ACCESS_TOKEN']
        dbx = dropbox.Dropbox(access_token)
        account = dbx.users_get_current_account()
        _logger.info('Dropbox authenticate successfully as {0}'.
                     format(account.name.display_name))
        global DBX
        DBX = dbx
    except KeyError as e:
        _logger.error(
            'Missing or wrong config format in ./config.ini {}'.format(e))
        return False
    except (AuthError, BadInputError) as e:
        _logger.error('Dropbox authenticate failed {}'.format(e))
        return False

    # check backup paths
    try:
        backup_paths = config['DEFAULT']['BACKUP_PATHS']
        backup_paths = backup_paths.split()
        if not backup_paths:
            _logger.warning('No file paths to backup.')
            return False

        path_not_exists = []
        expand_backup_paths = []
        for path in backup_paths:
            expand_path = os.path.expanduser(path)
            expand_backup_paths.append(expand_path)
            if not os.path.exists(expand_path):
                path_not_exists.append(path)

        if path_not_exists:
            _logger.error('These paths are not exists: {}'.
                          format(', '.join(path_not_exists)))
            return False

        global BACKUP_PATHS
        BACKUP_PATHS = expand_backup_paths
    except KeyError:
        _logger.error('Missing or wrong config format in ./config.ini')
        return False

    return True


def get_recursive_files(path):
    if os.path.isfile(path):
        return [path]

    paths = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            paths.append(os.path.join(path, name))

    return paths


def upload_file(path):
    with open(path, 'rb') as f:
        try:
            _logger.info('Uploading {} ...'.format(path))
            DBX.files_upload(f.read(), path, mode=WriteMode('overwrite'))
        except ApiError as e:
            _logger.error('Error occurred: {}'.format(e))


def delete_file(path):
    try:
        _logger.info('Remove {} ...'.format(path))
        DBX.files_delete(path)
    except ApiError as e:
        _logger.error('Error occurred: {}'.format(e))


def backup(BACKUP_PATHS):
    upload_files = []
    for path in BACKUP_PATHS:
        for p in get_recursive_files(path):
            # # threading seems not work
            # thread = threading.Thread(target=upload_file, args=[p])
            # thread.daemon = True
            # thread.start()

            upload_file(p)
            upload_files.append(p)

    remove_files = []
    for entry in DBX.files_list_folder(path='', recursive=True).entries:
        if isinstance(entry, dropbox.files.FileMetadata) and \
                entry.path_display not in upload_files:
            remove_files.append(entry.path_display)

    if remove_files:
        for p in remove_files:
            # thread = threading.Thread(target=delete_file, args=[p])
            # thread.daemon = True
            # thread.start()

            delete_file(p)

    return True


if __name__ == '__main__':
    if not validate_config():
        sys.exit(1)

    backup(BACKUP_PATHS)
