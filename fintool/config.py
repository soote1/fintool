import json


DEFAULT_PATH = '~/.fintool/config.json'


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
        keys = key.split('.')
        value = cls.__cfg
        for k in keys:
            value = value[k]
        return value

    @classmethod
    def set(cls, key, val):
        """
        Set a value for the given key. If the inner keys doesn't exist, then
        create the corresponding objects.
        """
        keys = key.split('.')
        node = cls.__cfg
        for k in keys[:-1]:
            try:
                node = node[k]
            except KeyError:
                node[k] = {}
                node = node[k]
        node[keys[-1]] = val

    @classmethod
    def load_cfg(cls, path=DEFAULT_PATH):
        """
        Load a json config file from the given path. If no path provided, then
        load the config from the default home dir location.
        """
        with open(path, 'r') as f:
            return json.loads(f.read())

    @classmethod
    def dump_config(cls, path=DEFAULT_PATH):
        """
        Write the config object into a file.
        """
        with open(path, 'w') as f:
            f.write(cls.__cfg)
