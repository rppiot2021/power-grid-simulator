"""
backend module implementation for file logging
"""

from os.path import join

from log_manager import LogManager
from pathlib import Path
import yaml


class FileManager(LogManager):
    # DEFAULT_FILE_PATH = "temp_file.db"
    # DEFAULT_FILE_FOLDER = "file_log"
    # DEFAULT_ARCHIVE_FOLDER = "file_archive"

    ARE_CONSTANTS_LOADED = False

    @staticmethod
    def _init_constants():
        FileManager.ARE_CONSTANTS_LOADED = True

        with open("conf.yaml", "r") as stream:

            # try:
            t = yaml.safe_load(stream)["file_manager"]

            FileManager.DEFAULT_FILE_PATH = t["default_file_path"]
            FileManager.DEFAULT_FILE_FOLDER = t["default_file_folder"]
            FileManager.DEFAULT_ARCHIVE_FOLDER = t["default_archive_folder"]

            # except yaml.YAMLError as exc:
            #     print(exc)

    # def _constants_init(
    #     self,
    #     file_path=t["default_file_path"],
    #     file_folder=t["default_file_folder"],
    #     archive_folder=t["default_archive_folder"],
    # ):
    #     pass

    def __init__(
        self,
        file_path=None,
        file_folder=None,
        archive_folder=None
    ):

        # if not FileManager.ARE_CONSTANTS_LOADED:
        #     print("init")
        #     FileManager._init_constants()

        with open("conf.yaml", "r") as stream:

            # try:
            t = yaml.safe_load(stream)["file_manager"]

            self.DEFAULT_FILE_PATH = file_path or t["default_file_path"]
            self.DEFAULT_FILE_FOLDER =file_folder or  t["default_file_folder"]
            self.DEFAULT_ARCHIVE_FOLDER =archive_folder or t["default_archive_folder"]

            # print(self.DEFAULT_FILE_FOLDER)
            # print(self.DEFAULT_FILE_PATH)
            # print(self.DEFAULT_ARCHIVE_FOLDER)


            # self.DEFAULT_FILE_PATH = t["default_file_path"]
            # self.DEFAULT_FILE_FOLDER = t["default_file_folder"]
            # self.DEFAULT_ARCHIVE_FOLDER = t["default_archive_folder"]


        Path(self.DEFAULT_FILE_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(self.DEFAULT_ARCHIVE_FOLDER).mkdir(parents=True, exist_ok=True)

        self.file_full_path = join(self.DEFAULT_FILE_FOLDER, self.DEFAULT_FILE_PATH)

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

    with FileManager("a", "b", "c") as file:
        file.write("t1", "t2")
        print(file.DEFAULT_FILE_FOLDER)
        print(file.DEFAULT_FILE_PATH)
        print(file.DEFAULT_ARCHIVE_FOLDER)

    with FileManager() as file:
        file.write("t1", "t2")
        print(file.DEFAULT_FILE_FOLDER)
        print(file.DEFAULT_FILE_PATH)
        print(file.DEFAULT_ARCHIVE_FOLDER)
