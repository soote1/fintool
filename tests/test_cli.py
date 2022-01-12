import unittest
import fintool.cli


class TestCLI(unittest.TestCase):

    def test_parse_add_cmd(self):
        expected = {
            'action': 'add',
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
        expected = {'action': 'remove', 'id': 'aasd'}

        cmd = ["remove", "--id", "aasd"]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_list_cmd(self):
        expected = {
            'action': 'list',
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
            'action': 'show',
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
            'action': 'edit',
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

    def test_execute_cmd(self):
        pass  # TODO

    def test_init(self):
        pass  # TODO
