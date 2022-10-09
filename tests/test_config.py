import unittest

from fintool.config import ConfigManager


class TestConfig(unittest.TestCase):
    """
    ConfigManager test suite.
    """
    def test_get_value(self):
        """
        Make sure that the config manager returns the expected value.
        """
        expected = 3
        initial_cfg = {'a': 1, 'b': 2, 'c': {'d': {'e': 3}}}

        ConfigManager.init(initial_cfg)
        actual = ConfigManager.get('c.d.e')

        self.assertEqual(actual, expected)

    def test_set_value(self):
        """
        Make sure that the config manager sets the value in the corresponding
        key and in the expected level of the parent object.
        """
        expected = {'a': 1, 'b': 2, 'c': {'d': {'e': 3}}}
        initial_cfg = {'a': 1, 'b': 2}

        ConfigManager.init(initial_cfg)
        ConfigManager.set('c.d.e', 3)
        actual = ConfigManager.get_cfg()

        self.assertEqual(actual, expected)

    def test_append_value(self):
        """
        Make sure that the config manager appends the value in the
        corresponding key and in the expected level of the parent object.
        """
        expected = {'a': 1, 'b': 2, 'c': {'d': {'e': [2, 3]}}}
        initial_cfg = {'a': 1, 'b': 2, 'c': {'d': {'e': [2]}}}

        ConfigManager.init(initial_cfg)
        ConfigManager.append('c.d.e', 3)
        actual = ConfigManager.get_cfg()

        self.assertEqual(actual, expected)
