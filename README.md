# Dropbox Backup

Backup local files to Dropbox

## Configuration

- Clone `config.ini.example` to `config.ini`
    - `ACCESS_TOKEN`: Create an app with access type `App folder` and get access token from https://www.dropbox.com/developers/apps
    - `BACKUP_PATHS`: Specify files or dirs to backup, separate line by line
```
BACKUP_PATHS = ~/first_file
    ~/first_dir
    /var/second_dir
```

## Running

- Install requirement and run the script
```
pip3 install -r requirement.txt
chmod +x dbak.py && python3 dbak.py
```
