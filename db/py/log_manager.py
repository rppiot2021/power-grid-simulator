from shutil import copy
from datetime import datetime
import time

import yaml
import os
from pathlib import Path
from os.path import join


class LogManager:

    def __init__(
        self,
        filename=None,
        prefix=None,
        base_folder=None,
        base_filename=None,
        archive_folder=None
    ):

        # if prefix == None use default
        # if prefix == "" -> no preifx
        # if prefix == anything else -> use that

        with open("conf.yaml", "r") as stream:

            t = yaml.safe_load(stream)[filename]

            prefix = prefix or t["prefix"]

            if prefix == "None":
                print("no prefix")

                # for joining
                prefix = ""

            else:
                print("prefix exist", prefix)

                if not os.path.exists(prefix):
                    os.makedirs(prefix)

            self.prefix = prefix

            nme = filename.split("_")[0]

            self.default_base_filename = base_filename or t[
                f"default_{nme}_filename"]

            self.default_base_folder = base_folder or join(prefix, t[
                f"default_{nme}_folder"])
            self.default_archive_folder = archive_folder or join(prefix, t[
                f"default_archive_folder"])

        Path(self.default_base_folder).mkdir(parents=True, exist_ok=True)
        Path(self.default_archive_folder).mkdir(parents=True, exist_ok=True)

        self.base_full_path = join(self.default_base_folder,
                                 self.default_base_filename)

    def _create_archive(self, num_of_rows):
        if num_of_rows >= self.log_buffer:

            print("archiving")

            current_time = str(
                datetime.fromtimestamp(time.time())).replace(" ", "_")
            full_path = join(self.default_archive_folder, current_time + ".db")
            open(full_path, "w+")
            copy(self.base_full_path, full_path)

            return True

        return False

    def __enter__(self):
        return self

    def _close(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._close()
