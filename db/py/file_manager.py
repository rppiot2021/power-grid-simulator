"""
backend module implementation for file logging
"""

from os.path import join

from log_manager import LogManager
from pathlib import Path
import yaml


class FileManager(LogManager):
    DEFAULT_FILE_PATH = "temp_file.db"
    DEFAULT_FILE_FOLDER = "file_log"

    DEFAULT_ARCHIVE_FOLDER = "file_archive"

    ARE_CONSTANTS_LOADED = False

    @staticmethod
    def _init_constants():
        FileManager.ARE_CONSTANTS_LOADED = True

        with open("conf.yaml", "r") as stream:

            t = None

            try:
                t = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)

                return

            print(t)

            t = t["file_manager"]

            FileManager.DEFAULT_FILE_PATH = t["default_file_path"]
            FileManager.DEFAULT_FILE_FOLDER = t["default_file_folder"]
            FileManager.DEFAULT_ARCHIVE_FOLDER = t["default_archive_folder"]
            #
            #
            #
            #
            #
            # FileManager.DEFAULT_FILE_PATH = "temp_file.db"
            # FileManager.DEFAULT_FILE_FOLDER = "file_log"
            # FileManager.DEFAULT_ARCHIVE_FOLDER = "file_archive"
            # #
            #
            # t = f"{FileManager.DEFAULT_FILE_FOLDER=}".split("=")
            # [0]
            # t = t.split("=")[0]
            # print(t)

            # self.file_path = DEFAULT_FILE_PATH,
            # self.file_folder = DEFAULT_FILE_FOLDER,
            # self.archive_folder = DEFAULT_ARCHIVE_FOLDER

    def __init__(
        self,
        file_path=DEFAULT_FILE_PATH,
        file_folder=DEFAULT_FILE_FOLDER,
        archive_folder=DEFAULT_ARCHIVE_FOLDER
    ):

        if not FileManager.ARE_CONSTANTS_LOADED:
            print("init")
            FileManager._init_constants()


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

    with FileManager() as file:
        file.write("t1", "t2")
        print(file.DEFAULT_FILE_FOLDER)
        print(file.DEFAULT_FILE_PATH)
        print(file.DEFAULT_ARCHIVE_FOLDER)

    with FileManager() as file:
        file.write("t1", "t2")
        print(file.DEFAULT_FILE_FOLDER)
        print(file.DEFAULT_FILE_PATH)
        print(file.DEFAULT_ARCHIVE_FOLDER)
