# fintool
A linux CLI app to help you manage your finances

## Usage
```
python3 -m fintool.cli --help
usage: cli.py [-h] {txs,tags} ...

positional arguments:
  {txs,tags}
    txs       Manage transactions
    tags      Manage tags

optional arguments:
  -h, --help  show this help message and exit

python3 -m fintool.cli txs --help
usage: cli.py txs [-h] {add,remove,list,stats,edit} ...

positional arguments:
  {add,remove,list,stats,edit}
    add                 Add a transaction
    remove              Remove a transaction
    list                List transactions
    stats               show different types of stats about transactions
    edit                Edit a transaction

optional arguments:
  -h, --help            show this help message and exit

python3 -m fintool.cli tags --help
usage: cli.py tags [-h] {add,edit,remove,list} ...

positional arguments:
  {add,edit,remove,list}
    add                 Add a new tag to db
    edit                Update the values of a an existing tag
    remove              Remove a given tag from db
    list                List all tags in db

optional arguments:
  -h, --help            show this help message and exit

```
