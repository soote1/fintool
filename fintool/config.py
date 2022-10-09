import json
import pathlib


DEFAULT_PATH = '~/.fintool/config.json'


class MissingCfgFileError(Exception):
    """Raised when the cfg file doesn't exists."""


class ConfigManager:
    """
    A helper class to keep the config in memory.
    """
    __cfg = dict()

    @classmethod
    def init(cls, cfg=None):
        cls.__cfg = cfg if cfg else cls.load_cfg()

    @classmethod
    def get_cfg(cls):
        """
        Return the cfg object.
        """
        return cls.__cfg

    @classmethod
    def get(cls, key):
        """
        Get the corresponding value for the given key. If the key is composite,
        then go into the cfg object and return the value corresponding to the
        last part.
        """
        if not cls.__cfg:
            cls.__cfg = cls.load_cfg()

        keys = key.split('.')
        value = cls.__cfg
        for k in keys:
            value = value[k]
        return value

    @classmethod
    def traverse_path(cls, path, create_inner=False):
        """
        Traverse the cfg object by following the given path. If create_inner is
        True, then create missing nodes. Return the last node in the path.
        """
        current_node = cls.__cfg
        for k in path:
            try:
                current_node = current_node[k]
            except KeyError as e:
                if create_inner:
                    current_node[k] = {}
                    current_node = current_node[k]
                else:
                    raise e
        return current_node

    @classmethod
    def set(cls, key, val):
        """
        Set a value for the given key. If the inner keys doesn't exist, then
        create the corresponding objects.
        """
        if not cls.__cfg:
            cls.__cfg = cls.load_cfg()

        keys = key.split('.')
        node = cls.traverse_path(keys[:-1], create_inner=True)
        node[keys[-1]] = val

    @classmethod
    def append(cls, key, val):
        """
        Append the value to given key.
        """
        keys = key.split('.')
        node = cls.traverse_path(keys[:-1], create_inner=True)
        node[keys[-1]].append(val)

    @classmethod
    def load_cfg(cls, path=DEFAULT_PATH):
        """
        Load a json config file from the given path. If no path provided, then
        load the config from the default home dir location.
        """
        try:
            with pathlib.Path(path).expanduser().open('r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            cls.dump_config()

    @classmethod
    def dump_config(cls, path=DEFAULT_PATH):
        """
        Write the config object into a file.
        """
        with pathlib.Path(path).expanduser().open('w+') as f:
            f.write(json.dumps(cls.__cfg))
