import unittest
import fintool.cli
import fintool.actions


class TestCLI(unittest.TestCase):

    def test_parse_add_tx_cmd(self):
        expected = {
            'cmd': 'txs',
            'action': 'add',
            'type': 'some',
            'date': 'other',
            'amount': '12.12',
            'tags': 'a,b,c'
        }

        cmd = [
            "txs",
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
        expected = {
            'cmd': 'txs',
            'action': 'remove',
            'id': '1',
            'date': '2020-01-01'
        }

        cmd = ['txs', 'remove', '--id', '1', '--date', '2020-01-01']

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_list_cmd(self):
        expected = {
            'cmd': 'txs',
            'action': 'list',
            'type': 'income',
            'tags': 'a,b,c',
            'amount': '12-32',
            'from': '2020-01-01',
            'to': '2020-02-01'
        }

        cmd = [
            "txs",
            "list",
            "--type",
            "income",
            "--from",
            "2020-01-01",
            "--to",
            "2020-02-01",
            "--amount",
            "12-32",
            "--tags",
            "a,b,c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_stats_cmd(self):
        expected = {
            'cmd': 'txs',
            'action': 'stats',
            'statstype': 'overall_summary',
            'draw': 'pie',
            'type': 'income',
            'from': '2020-01-01',
            'to': '2020-02-01',
            'tags': 'a,b,c',
            'amount': '12-32'
        }

        cmd = [
            "txs",
            "stats",
            "--statstype",
            "overall_summary",
            "--draw",
            "pie",
            "--type",
            "income",
            "--from",
            "2020-01-01",
            "--to",
            "2020-02-01",
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
            'cmd': 'txs',
            'action': 'edit',
            'id': 'some-id',
            'type': 'some-type',
            'olddate': '2020-01-01',
            'date': '2020-02-01',
            'amount': '123.2',
            'tags': 'a,b,c'
        }

        cmd = [
            "txs",
            "edit",
            "--id",
            "some-id",
            "--type",
            "some-type",
            "--olddate",
            "2020-01-01",
            "--date",
            "2020-02-01",
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
        expected_cmd = fintool.cli.Command("txs.add", expected_actions, None)
        args = {'cmd': 'txs', 'action': 'add', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_remove_cmd(self):
        expected_actions = [fintool.actions.RemoveTransaction]
        expected_cmd = fintool.cli.Command(
            "txs.remove",
            expected_actions,
            None
        )
        args = {'cmd': 'txs', 'action': 'remove', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_list_cmd(self):
        expected_actions = [
            fintool.actions.CreateFilters,
            fintool.actions.GetTransactions,
            fintool.actions.PrintTransactions
        ]

        expected_cmd = fintool.cli.Command("txs.list", expected_actions, None)
        args = {'cmd': 'txs', 'action': 'list', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    @unittest.skip("not implemented")
    def test_create_show_cmd(self):
        pass  # TODO

    def test_create_edit_cmd(self):
        expected_actions = [
            fintool.actions.CreateTransaction,
            fintool.actions.UpdateTransaction
        ]
        expected_cmd = fintool.cli.Command("txs.edit", expected_actions, None)

        args = {'cmd': 'txs', 'action': 'edit', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    @unittest.skip("not implemented")
    def test_execute_cmd(self):
        pass  # TODO

    @unittest.skip("not implemented")
    def test_init(self):
        pass  # TODO

    def test_create_add_tag_cmd(self):
        expected_actions = [
            fintool.actions.CreateTag,
            fintool.actions.AddTag
        ]
        expected_cmd = fintool.cli.Command("tags.add", expected_actions, None)

        args = {'cmd': 'tags', 'action': 'add', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_edit_tag_cmd(self):
        expected_actions = [
            fintool.actions.CreateTag,
            fintool.actions.EditTag
        ]
        expected_cmd = fintool.cli.Command("tags.edit", expected_actions, None)

        args = {'cmd': 'tags', 'action': 'edit', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_remove_tag_cmd(self):
        expected_actions = [
            fintool.actions.RemoveTag
        ]
        expected_cmd = fintool.cli.Command(
            "tags.remove",
            expected_actions,
            None
        )

        args = {'cmd': 'tags', 'action': 'remove', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_list_tags_cmd(self):
        expected_actions = [
            fintool.actions.GetTags,
            fintool.actions.PrintTags
        ]
        expected_cmd = fintool.cli.Command(
            "tags.list",
            expected_actions,
            None
        )

        args = {'cmd': 'tags', 'action': 'list', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_parse_add_tag_cmd(self):
        expected = {
            'cmd': 'tags',
            'action': 'add',
            'concept': 'some_concept',
            'tags': 'a|b|c'
        }

        cmd = [
            "tags",
            "add",
            "--concept",
            "some_concept",
            "--tags",
            "a|b|c"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_edit_tag_cmd(self):
        expected = {
            'cmd': 'tags',
            'action': 'edit',
            'concept': 'some_concept',
            'tags': 'a|b|c',
            'tagid': 'some_id'
        }

        cmd = [
            "tags",
            "edit",
            "--concept",
            "some_concept",
            "--tags",
            "a|b|c",
            "--tagid",
            "some_id"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_remove_tag_cmd(self):
        expected = {
            'cmd': 'tags',
            'action': 'remove',
            'tagid': 'some_id'
        }

        cmd = [
            "tags",
            "remove",
            "--tagid",
            "some_id"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_list_tags_cmd(self):
        expected = {'cmd': 'tags', 'action': 'list'}

        cmd = ["tags", "list"]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)
