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

    def test_parse_stats_cmd(self):
        expected = {
            'cmd': 'stats',
            'statstype': 'overall_summary',
            'draw': 'pie',
            'type': 'income',
            'date': 'sad-asdasd',
            'tags': 'a,b,c',
            'amount': '12-32'
        }

        cmd = [
            "stats",
            "--statstype",
            "overall_summary",
            "--draw",
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

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_remove_cmd(self):
        expected_actions = [fintool.actions.RemoveTransaction]
        expected_cmd = fintool.cli.Command("remove", expected_actions, None)
        args = {'cmd': 'remove', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_list_cmd(self):
        expected_actions = [
            fintool.actions.CreateFilters,
            fintool.actions.GetTransactions,
            fintool.actions.PrintTransactions
        ]

        expected_cmd = fintool.cli.Command("list", expected_actions, None)
        args = {'cmd': 'list', 'other': None}
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
        expected_cmd = fintool.cli.Command("edit", expected_actions, None)

        args = {'cmd': 'edit', 'other': None}
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
        expected_cmd = fintool.cli.Command("add_tag", expected_actions, None)

        args = {'cmd': 'add_tag', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_edit_tag_cmd(self):
        expected_actions = [
            fintool.actions.CreateTag,
            fintool.actions.EditTag
        ]
        expected_cmd = fintool.cli.Command("edit_tag", expected_actions, None)

        args = {'cmd': 'edit_tag', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_remove_tag_cmd(self):
        expected_actions = [
            fintool.actions.RemoveTag
        ]
        expected_cmd = fintool.cli.Command(
            "remove_tag",
            expected_actions,
            None
        )

        args = {'cmd': 'remove_tag', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_create_list_tags_cmd(self):
        expected_actions = [
            fintool.actions.GetTags,
            fintool.actions.PrintTags
        ]
        expected_cmd = fintool.cli.Command(
            "list_tags",
            expected_actions,
            None
        )

        args = {'cmd': 'list_tags', 'other': None}
        actual = fintool.cli.CLI().create_cmd(args)

        self.assertEqual(actual.cmd, expected_cmd.cmd)
        self.assertEqual(actual.actions, expected_cmd.actions)

    def test_parse_add_tag_cmd(self):
        expected = {
            'cmd': 'add_tag',
            'concept': 'some_concept',
            'tags': 'a|b|c'
        }

        cmd = [
            "add_tag",
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
            'cmd': 'edit_tag',
            'concept': 'some_concept',
            'tags': 'a|b|c',
            'tagid': 'some_id'
        }

        cmd = [
            "edit_tag",
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
            'cmd': 'remove_tag',
            'tagid': 'some_id'
        }

        cmd = [
            "remove_tag",
            "--tagid",
            "some_id"
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)

    def test_parse_list_tags_cmd(self):
        expected = {
            'cmd': 'list_tags',
        }

        cmd = [
            "list_tags",
        ]

        cli = fintool.cli.CLI()
        actual = cli.parse_args(cmd)

        self.assertEqual(actual, expected)
