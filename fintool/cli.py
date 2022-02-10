import os
import sys
import json
import pathlib
import argparse

from fintool.actions import (
    CreateTransaction,
    SaveTransaction,
    CreateFilters,
    GetTransactions,
    PrintTransactions,
    RemoveTransaction,
    UpdateTransaction
)
from fintool.logging import LoggingHelper


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
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._logger.debug('setting up parser helper')
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
        self._logger.debug('parsing arguments %s', arguments)
        args = self.parser.parse_args(arguments)
        return vars(args)


class Command:
    def __init__(self, cmd, actions, data):
        self.cmd = cmd
        self.actions = actions
        self.data = data

    def __repr__(self):
        return f"cmd: {self.cmd} actions: {self.actions} data: {self.data}"


class CommandProcessor:
    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def process(self, cmd):
        """Execute a list of actions from
        a given command in sequential order.

        Args:
            cmd (Command): The command to be processed
            data (list): The list of associated actions
        """
        self._logger.debug('processing cmd: %s', cmd)
        for action in cmd.actions:
            action().exec(cmd.data)


SUPPORTED_CMDS = {
    ADD_CMD: [CreateTransaction, SaveTransaction],
    REMOVE_CMD: [RemoveTransaction],
    LIST_CMD: [CreateFilters, GetTransactions, PrintTransactions],
    SHOW_CMD: [],
    EDIT_CMD: [CreateTransaction, UpdateTransaction],
}


class UnsupportedCmdError(Exception):
    pass


class CLI:

    def __init__(self):
        """Load configuration from json file and
        initialize args parser object.
        """
        # get log level from env var or set info as default
        LoggingHelper.set_log_level(os.getenv('FINTOOL_LOGLEVEL', 'info'))
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

        BASE_DIR = pathlib.Path(__file__).parent
        cli_cfg_path = BASE_DIR.joinpath(CLI_CFG_FILE).resolve()
        self._logger.debug('loading cli config from %s', cli_cfg_path)
        with cli_cfg_path.open() as cfg_file:
            self._cli_cfg = json.loads(cfg_file.read())

        self.args_parser = ArgsParser(self._cli_cfg[ARGS_PARSER_CFG])
        self.cmd_processor = CommandProcessor()

    def parse_args(self, args):
        """
        Use arguments parser object to parse args and
        return result object.
        """
        self._logger.debug('parsing arguments: %s', args)
        return self.args_parser.parse(args)

    def create_cmd(self, args):
        """Create a Command object from given cmd id.

        Raise UnsupportedCmdError if cmd_id contains an invalid value.

        Args:
            args (dict): Parsed cli arguments.
        """
        self._logger.debug('creating command from args: %s', args)
        try:
            cmd_id = args[CLI_CMD]
            # cmd data consists of all key-values in args except cmd id
            cmd_data = {k: args[k] for k in args.keys() - {CLI_CMD}}
            cmd_actions = SUPPORTED_CMDS[cmd_id]
            return Command(cmd_id, cmd_actions, cmd_data)
        except KeyError as key_error:
            raise UnsupportedCmdError("Unsupported command: %s", key_error)

    def run(self, args):
        """Main cli method that starts by parsing
        provided cli arguments, next creates a command
        object and calls the process() method.

        Args:
            args (list): A list of cli arguments
        """
        self._logger.debug('running cli with: %s', args)
        try:
            parsed_args = self.parse_args(args)
            cmd = self.create_cmd(parsed_args)
            self.cmd_processor.process(cmd)
        except Exception as exception:
            self._logger.error(
                'an error ocurred while running command: %s',
                exception
            )

            sys.exit(1)


if __name__ == "__main__":
    cli_obj = CLI()
    cli_obj.run(sys.argv[1:])
