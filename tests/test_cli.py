import unittest
import fintool.cli


class TestCLI(unittest.TestCase):

    def test_parse_add_cmd(self):
        expected = {
            'cmd': 'add',
            'type': 'some',
            'date': 'other',
            'amount': '12.12',
            'tags': 'a,b,c'
        }

        cmd = [
            "add",
            "--type",
            "some",
            "--date",
            "other",
            "--amount",
            "12.12",
            "--tags",
            "a,b,c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_remove_cmd(self):
        expected = {'cmd': 'remove', 'id': 'aasd'}

        cmd = ["remove", "--id", "aasd"]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_list_cmd(self):
        expected = {
            'cmd': 'list',
            'type': 'income',
            'date': 'sad-asdasd',
            'tags': 'a,b,c',
            'amount': '12-32'
        }

        cmd = [
            "list",
            "--type",
            "income",
            "--date",
            "sad-asdasd",
            "--amount",
            "12-32",
            "--tags",
            "a,b,c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_show_cmd(self):
        expected = {
            'cmd': 'show',
            'chart_type': 'pie',
            'type': 'income',
            'date': 'sad-asdasd',
            'tags': 'a,b,c',
            'amount': '12-32'
        }

        cmd = [
            "show",
            "--chart-type",
            "pie",
            "--type",
            "income",
            "--date",
            "sad-asdasd",
            "--amount",
            "12-32",
            "--tags",
            "a,b,c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_edit_cmd(self):
        expected = {
            'cmd': 'edit',
            'id': 'some-id',
            'type': 'some-type',
            'date': 'some-date',
            'amount': '123.2',
            'tags': 'a,b,c'
        }

        cmd = [
            "edit",
            "--id",
            "some-id",
            "--type",
            "some-type",
            "--date",
            "some-date",
            "--amount",
            "123.2",
            "--tags",
            "a,b,c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_create_add_cmd(self):
        expected = fintool.cli.Command("add", [])
        actual = fintool.cli.CLI().create_cmd("add")

        self.assertEqual(actual._cmd, expected._cmd)
        self.assertEqual(actual._actions, expected._actions)

    def test_create_remove_cmd(self):
        expected = fintool.cli.Command("remove", [])
        actual = fintool.cli.CLI().create_cmd("remove")

        self.assertEqual(actual._cmd, expected._cmd)
        self.assertEqual(actual._actions, expected._actions)

    def test_create_list_cmd(self):
        expected = fintool.cli.Command("list", [])
        actual = fintool.cli.CLI().create_cmd("list")

        self.assertEqual(actual._cmd, expected._cmd)
        self.assertEqual(actual._actions, expected._actions)

    def test_create_show_cmd(self):
        expected = fintool.cli.Command("show", [])
        actual = fintool.cli.CLI().create_cmd("show")

        self.assertEqual(actual._cmd, expected._cmd)
        self.assertEqual(actual._actions, expected._actions)

    def test_create_edit_cmd(self):
        expected = fintool.cli.Command("edit", [])
        actual = fintool.cli.CLI().create_cmd("edit")

        self.assertEqual(actual._cmd, expected._cmd)
        self.assertEqual(actual._actions, expected._actions)

    def test_execute_cmd(self):
        pass  # TODO

    def test_init(self):
        pass  # TODO
