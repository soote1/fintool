import unittest
import fintool.cli
import fintool.actions


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
        expected_actions = [
            fintool.actions.CreateTransaction,
            fintool.actions.SaveTransaction
        ]
        expected_cmd = fintool.cli.Command("add", expected_actions, None)
        args = {'cmd': 'add', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual._cmd, expected_cmd._cmd)
        self.assertEqual(actual._actions, expected_cmd._actions)

    @unittest.skip("not implemented")
    def test_create_remove_cmd(self):
        pass  # TODO

    def test_create_list_cmd(self):
        expected_actions = [
            fintool.actions.CreateFilters,
            fintool.actions.GetTransactions,
            fintool.actions.PrintTransactions
        ]

        expected_cmd = fintool.cli.Command("list", expected_actions, None)
        args = {'cmd': 'list', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual._cmd, expected_cmd._cmd)
        self.assertEqual(actual._actions, expected_cmd._actions)

    @unittest.skip("not implemented")
    def test_create_show_cmd(self):
        pass  # TODO

    @unittest.skip("not implemented")
    def test_create_edit_cmd(self):
        pass  # TODO

    @unittest.skip("not implemented")
    def test_execute_cmd(self):
        pass  # TODO

    @unittest.skip("not implemented")
    def test_init(self):
        pass  # TODO
