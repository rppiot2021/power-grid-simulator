import os
from os.path import join
from pathlib import Path

import yaml

from log_manager import LogManager


class FileManager(LogManager):

    def __init__(
        self,
        prefix=None,
        file_filename=None,
        file_folder=None,
        archive_folder=None
    ):

        super().__init__("file_manager", prefix, file_folder, file_filename, archive_folder)

        # with open("conf.yaml", "r") as stream:
        #     t = yaml.safe_load(stream)["file_manager"]
        #
        #     prefix = t["prefix"]
        #
        #     if prefix == "None":
        #         print("no prefix")
        #
        #         # for joining
        #         prefix = ""
        #
        #     else:
        #         print("prefix exist", prefix)
        #
        #         if not os.path.exists(prefix):
        #             os.makedirs(prefix)
        #
        #     self.default_file_path = file_filename or t["default_file_filename"]
        #
        #     self.default_file_folder = file_folder or join(prefix, t[
        #         "default_file_folder"])
        #     self.default_archive_folder = archive_folder or join(prefix, t[
        #         "default_archive_folder"])
        #
        # Path(self.default_file_folder).mkdir(parents=True, exist_ok=True)
        # Path(self.default_archive_folder).mkdir(parents=True, exist_ok=True)
        #
        self.file_full_path = join(self.default_base_folder,
                                   self.default_base_filename)

        self.file = open(self.file_full_path, "a")

    def _close(self):
        self.file.close()

    def write(self, *data):
        self.file.write(str(data) + "\n")

        self._cleanup()

    def _cleanup(self):
        """copy and delete from current file, use 100 inters"""
        raise NotImplementedError


if __name__ == '__main__':
    # with FileManager("a", "b", "c") as file:
    #     file.write("t1", "t2")
    #     print(file.default_file_folder)
    #     print(file.default_file_path)
    #     print(file.default_archive_folder)

    with FileManager() as file:
        file.write("t1", "t2")
        print(file.default_file_folder)
        print(file.default_file_path)
        print(file.default_archive_folder)
