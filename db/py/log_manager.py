import yaml
import os
from pathlib import Path
from os.path import join


class LogManager:

    # def __init__(self, is_opened):
    #     self.is_opened = is_opened
    #
    # def check_connection(self):
    #     if not self.is_opened:
    #         raise PermissionError("connection closed or not established")

    # def load_paths(self, prefix, base_folder, base_filename, archive_folder):

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
            # t = yaml.safe_load(stream)["database_manager"]
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

            nme = filename.split("_")[0]

            self.default_base_filename = base_filename or t[
                f"default_{nme}_filename"]

            self.default_base_folder = base_folder or join(prefix, t[
                f"default_{nme}_folder"])
            self.default_archive_folder = archive_folder or join(prefix, t[
                f"default_{nme}_folder"])

        Path(self.default_base_folder).mkdir(parents=True, exist_ok=True)
        Path(self.default_archive_folder).mkdir(parents=True, exist_ok=True)

        self.db_full_path = join(self.default_base_folder,
                                 self.default_base_filename)

    def __str__(self):
        return self.is_opened

    def __enter__(self):
        return self

    def _close(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._close()
