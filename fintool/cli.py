import sys
import json
import pathlib
import argparse

from fintool.actions import CreateTransaction, SaveTransaction


SUBPARSERS = 'subparsers'
REQUIRED = 'required'
ID = 'id'
SUBPARSERS_CFGS = 'subparsers_cfgs'
NAME = 'name'
HELP = 'help'
ARGS = 'args'
PROGRAM_NAME = "fintool"
KWARGS = "kwargs"
CLI_CFG_FILE = "cli.json"
ARGS_PARSER_CFG = "argsparser"
CLI_CMD = "cmd"
ADD_CMD = "add"
REMOVE_CMD = "remove"
LIST_CMD = "list"
SHOW_CMD = "show"
EDIT_CMD = "edit"


class ArgsParser:
    """A helper class to validate arguments."""

    def __init__(self, config):
        """Initialize instance with given config."""

        self.load_parsers(config)

    def load_parsers(self, config):
        """Create arg parser object."""

        self.parser = argparse.ArgumentParser()
        if SUBPARSERS in config:
            self.load_subparsers(config[SUBPARSERS], self.parser)

    def load_subparsers(self, subparsers_config, parent_parser):
        """Add subparsers to parent parser recursively.
        Positional arguments:
            subparsers_config -- configuration dict for the current subparser
            parent_parser     -- parent object to add the parsers to.
        """

        # create subparsers
        subparsers = parent_parser.add_subparsers(dest=subparsers_config[ID])
        subparsers.required = subparsers_config[REQUIRED]
        for subparser_config in subparsers_config[SUBPARSERS_CFGS]:
            subparser = subparsers.add_parser(
                subparser_config[NAME], help=subparser_config[HELP])

            # load arguments for subparser
            for arg in subparser_config[ARGS]:
                if KWARGS in arg:
                    subparser.add_argument(arg[ID], **arg[KWARGS])
                else:
                    subparser.add_argument(arg[ID])

            if SUBPARSERS in subparser_config:
                self.load_subparsers(subparser_config[SUBPARSERS], subparser)

    def parse(self, arguments):
        """Parse a list of arguments and return a dictionary with the result.

        Positional arguments:
            arguments -- a list of strings representing arguments
        Return value:
            a dictionary with the result of argparse.ArgumentParser.parse_args
        """

        args = self.parser.parse_args(arguments)
        return vars(args)


class Command:
    def __init__(self, cmd, actions, data):
        self._cmd = cmd
        self._actions = actions
        self._data = data

    def __repr__(self):
        return f"cmd: {self._cmd} actions: {self._actions} data: {self._data}"


class CommandProcessor:
    def __init__(self):
        pass

    def process(self, cmd):
        """Execute a list of actions from
        a given command in sequential order.

        Args:
            cmd (Command): The command to be processed
            data (list): The list of associated actions
        """

        for action in cmd._actions:
            action().exec(cmd._data)


SUPPORTED_CMDS = {
    ADD_CMD: [CreateTransaction, SaveTransaction],
    REMOVE_CMD: [],
    LIST_CMD: [],
    SHOW_CMD: [],
    EDIT_CMD: [],
}


class UnsupportedCmdError(Exception):
    pass


class CLI:

    def __init__(self):
        """Load configuration from json file and
        initialize args parser object.
        """
        BASE_DIR = pathlib.Path(__file__).parent
        cli_cfg_path = BASE_DIR.joinpath(CLI_CFG_FILE).resolve()
        with cli_cfg_path.open() as f:
            self._cli_cfg = json.loads(f.read())

        self._args_parser = ArgsParser(self._cli_cfg[ARGS_PARSER_CFG])
        self._cmd_processor = CommandProcessor()

    def parse_args(self, args):
        """
        Use arguments parser object to parse args and
        return result object.
        """

        return self._args_parser.parse(args)

    def create_cmd(self, args):
        """Create a Command object from given cmd id.

        Raise UnsupportedCmdError if cmd_id contains an invalid value.

        Args:
            args (dict): Parsed cli arguments.
        """

        try:
            cmd_id = args[CLI_CMD]
            # cmd data consists of all key-values in args except cmd id
            cmd_data = {k: args[k] for k in args.keys() - {CLI_CMD}}
            cmd_actions = SUPPORTED_CMDS[cmd_id]
            return Command(cmd_id, cmd_actions, cmd_data)
        except KeyError as e:
            raise UnsupportedCmdError(f"Unsupported command: {e}")

    def run(self, args):
        """Main cli method that starts by parsing
        provided cli arguments, next creates a command
        object and calls the process() method.

        Args:
            args (list): A list of cli arguments
        """

        try:
            parsed_args = self.parse_args(args)
            cmd = self.create_cmd(parsed_args)
            self._cmd_processor.process(cmd)
        except Exception as e:
            print(e)
            sys.exit(1)


if __name__ == "__main__":
    cli_obj = CLI()
    cli_obj.run(sys.argv[1:])
