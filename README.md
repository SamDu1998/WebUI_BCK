# WebUI_BCK

## Project Description
This project is designed to periodically download a remote database file and keep backups for the last 7 days. It also includes a GUI to start and stop the download process.

## Features
- Downloads a remote database file every 4 hours.
- Keeps backups for the last 7 days.
- Deletes old backups automatically.
- Provides a GUI to start and stop the download process.

## Requirements
- Python 3.x
- `requests` library
- `tkinter` library

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/WebUI_BCK.git
    ```
2. Navigate to the project directory:
    ```sh
    cd WebUI_BCK
    ```
3. Install the required libraries:
    ```sh
    pip install requests
    ```

## Usage
1. Run the main script:
    ```sh
    python main.py
    ```
2. Use the GUI to start and stop the download process.

## Configuration
- **REMOTE_FILE_URL**: URL of the remote file to be downloaded.
- **BACKUP_DIR**: Directory where backups will be stored.
- **DOWNLOAD_INTERVAL**: Interval between downloads (in seconds).
- **KEEP_DAYS**: Number of days to keep backups.

## Download Executable
You can download the executable file from the [GitHub Releases](https://github.com/SamDu1998/WebUI_BCK/releases) page.

## License
This project is licensed under the MIT License.