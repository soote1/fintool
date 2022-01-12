import sys
import argparse


SUBPARSERS = 'subparsers'
REQUIRED = 'required'
ID = 'id'
SUBPARSERS_CFGS = 'subparsers_cfgs'
NAME = 'name'
HELP = 'help'
ARGS = 'args'
PROGRAM_NAME = "fintool"
KWARGS = "kwargs"


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
            subparsers_config -- the configuration dict for the current subparser
            parent_parser     -- the parent object to add the parsers to.
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
            a dictionary with the result of argparse.ArgumentParser.parse_args()
        """

        args = self.parser.parse_args(arguments)
        return vars(args)


class Command:
    def __init__(self, action, details):
        self._action = action
        self._details = details

    def __str__(self):
        return f"action: {self._action} details: {self._details}"


class CLI:

    def __init__(self):
        """Initialize cli object."""
        self._args_parser = ArgsParser(self.get_supported_commands())

    def get_supported_commands(self):
      """
      Define the supported commands in a dict
      that is compatible with ArgsParser and
      return it.
      """

      return {
          "prog": PROGRAM_NAME,
          "args": [],
          "subparsers": {
              "id": "action",
              "required": True,
              "subparsers_cfgs": [
                    {
                        "name": "add",
                        "help": "Add a transaction",
                        "args": [
                            {
                                "id": "--type",
                                "kwargs": {
                                    "required": True,
                                    "help": "Transaction type"
                                }
                            },
                            {
                                "id": "--date",
                                "kwargs": {
                                    "required": True,
                                    "help": "Transaction date"
                                }
                            },
                            {
                                "id": "--amount",
                                "kwargs": {
                                    "required": True,
                                    "help": "Transaction amount"
                                }
                            },
                            {
                                "id": "--tags",
                                "kwargs": {
                                    "required": True,
                                    "help": "A list of tags describing the transaction"
                                }
                            },
                        ],
                    },
                  {
                        "name": "remove",
                        "help": "Remove a transaction",
                        "args": [
                            {
                                "id": "--id",
                                "kwargs": {
                                    "help": "Transaction id",
                                    "required": True,
                                }
                            }
                        ]
                    },
                  {
                        "name": "list",
                        "help": "List transactions",
                        "args": [
                            {
                                "id": "--type",
                                "kwargs": {
                                    "help": "Transaction type to filter transactions"
                                }
                            },
                            {
                                "id": "--date",
                                "kwargs": {
                                    "help": "Date interval to filter transactions"
                                }
                            },
                            {
                                "id": "--tags",
                                "kwargs": {
                                    "help": "Tags to filter transactions"
                                }
                            },
                            {
                                "id": "--amount",
                                "kwargs": {
                                    "help": "Amount range to filter transactions"
                                }
                            },
                        ]
                    },
                  {
                        "name": "show",
                        "help": "Show transactions in some chart",
                        "args": [
                            {
                                "id": "--chart-type",
                                "kwargs": {
                                    "help": "The chart type to use to plot transactions",
                                    "required": True
                                }
                            },
                            {
                                "id": "--type",
                                "kwargs": {
                                    "help": "Transaction type to filter transactions"
                                }
                            },
                            {
                                "id": "--date",
                                "kwargs": {
                                    "help": "Date interval to filter transactions"
                                }
                            },
                            {
                                "id": "--tags",
                                "kwargs": {
                                    "help": "Tags to filter transactions"
                                }
                            },
                            {
                                "id": "--amount",
                                "kwargs": {
                                    "help": "Amount range to filter transactions"
                                }
                            },
                        ]
                    },
                  {
                        "name": "edit",
                        "help": "Edit a transaction",
                        "args": [
                            {
                                "id": "--id",
                                "kwargs": {
                                    "required": True,
                                    "help": "Transaction id"
                                }
                            },
                            {
                                "id": "--type",
                                "kwargs": {
                                    "help": "New transaction type"
                                }
                            },
                            {
                                "id": "--date",
                                "kwargs": {
                                    "help": "New transaction date"
                                }
                            },
                            {
                                "id": "--amount",
                                "kwargs": {
                                    "help": "New transaction amount"
                                }
                            },
                            {
                                "id": "--tags",
                                "kwargs": {
                                    "help": "New transaction tags"
                                }
                            },
                        ],
                    },
              ]
          }
      }

    def parse_args(self, args):
        """
        Use arguments parser object to parse args and
        return result object.
        """

        return self._args_parser.parse(args)

    def execute_cmd(self, cmd):
        print(cmd)

    def init(self, args):
      cmd = self.parse_args(args)
      self.execute_cmd(cmd)


if __name__ == "__main__":
    cli_obj = CLI()
    cli_obj.init(sys.argv[1:])
