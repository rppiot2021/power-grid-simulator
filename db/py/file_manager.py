import os
import time
from os.path import join
from pathlib import Path

import yaml

from log_manager import LogManager


class FileManager(LogManager):

    def __init__(
        self,
        log_buffer=15,
        prefix=None,
        file_filename=None,
        file_folder=None,
        archive_folder=None
    ):

        self.log_buffer = log_buffer

        super().__init__("file_manager", prefix, file_folder, file_filename, archive_folder)

        self.file_full_path = join(self.default_base_folder,
                                   self.default_base_filename)

        self.file = open(self.file_full_path, "a")

    def _close(self):
        self.file.close()

    def write(self, *data):
        self.file.write(str(data) + "\n")

        self._cleanup()

    def _cleanup(self):
        """
        copy and delete from current file, use 100 inters
        """
        num_of_rows = sum(1 for _ in open(self.base_full_path))

        is_created = self._create_archive(num_of_rows)

        if is_created:
            open(self.base_full_path, 'w').close()

        self.file = open(self.file_full_path, "a")


if __name__ == '__main__':
    # with FileManager("a", "b", "c") as file:
    #     file.write("t1", "t2")
    #     print(file.default_file_folder)
    #     print(file.default_file_path)
    #     print(file.default_archive_folder)

    with FileManager() as file:
        print(file.default_base_folder)
        print(file.default_base_filename)
        print(file.default_archive_folder)

        while True:
            time.sleep(1)
            file.write("t1", "t2")
            print("t")