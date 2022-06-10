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
