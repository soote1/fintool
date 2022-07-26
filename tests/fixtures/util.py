import os
import pathlib


PARENT_DIR = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent
TEST_DB_PATH = PARENT_DIR.joinpath('.fintool/')

def remove_dir(dir_path):
    """
    Recursively remove directory.
    """
    try:
        for f in dir_path.glob("*"):
            if f.is_file():
                f.unlink()
            else:
                remove_dir(f)
        dir_path.rmdir()
    except FileNotFoundError:
        pass  # db doesn't exists
