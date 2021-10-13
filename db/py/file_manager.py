"""
backend module implementation for file logging
"""

from os.path import join

from project.backend.log_manager import LogManager


class FileManager(LogManager):
    DEFAULT_FILE_PATH = "temp_file.db"
    DEFAULT_FILE_FOLDER = "file_log"

    DEFAULT_ARCHIVE_FOLDER = "file_archive"

    def __init__(self, file_path=DEFAULT_FILE_PATH,
                 file_folder=DEFAULT_FILE_FOLDER, archive_folder=DEFAULT_ARCHIVE_FOLDER):
        from pathlib import Path
        Path(file_folder).mkdir(parents=True, exist_ok=True)
        Path(archive_folder).mkdir(parents=True, exist_ok=True)

        self.file_full_path = join(file_folder, file_path)

        self.file = open(self.file_full_path, "a")
        super().__init__(True)

    def _close(self):
        self.check_connection()

        self.file.close()
        self.is_opened = False

    def write(self, *data):
        self.check_connection()

        self.file.write(str(data) + "\n")


if __name__ == '__main__':
    file = FileManager()
    file.write("t1", "t2")
    file._close()
