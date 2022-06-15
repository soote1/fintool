# fintool
A linux CLI app to help you manage your finances

## Usage
```
python3 -m fintool.cli --help

usage: cli.py [-h] {add,remove,list,stats,edit,add_tag,edit_tag,remove_tag,list_tags} ...

positional arguments:
  {add,remove,list,stats,edit,add_tag,edit_tag,remove_tag,list_tags}
    add                 Add a transaction
    remove              Remove a transaction
    list                List transactions
    stats               show different types of stats about transactions
    edit                Edit a transaction
    add_tag             Add a new tag to db
    edit_tag            Update the values of a an existing tag
    remove_tag          Remove a given tag from db
    list_tags           List all tags in db

optional arguments:
  -h, --help            show this help message and exit
```
