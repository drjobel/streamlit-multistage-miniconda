
import os
import shelve
from turpy.logger import log
from config import SHELVE_FILEPATH
from typing import List

#TODO: refactor as class


def shelf_persist(data: dict, table_key: str, SHELVE_FILEPATH: str = SHELVE_FILEPATH):
    """Persist dictionaries and objects in shelve. This is toy implementation. 
    Shelve will be open without `writeback=True`. Shelves do not track modifications
    to volatile objects, by default. That means if you change the contents of an item
    stored in the shelf, you must update the shelf explicitly by storing the item again.

    See: [docs](https://docs.python.org/3/library/shelve.html)
    See also: [PERSISTENT DICT WITH MULTIPLE STANDARD FILE FORMATS (PYTHON RECIPE)](https://code.activestate.com/recipes/576642/)
    
    :param
    :param data: data holding dictionary
    :param table_key: key to store the dictionary

    :Warning:  Because the `shelve` module is backed by `pickle`,
    it is insecure to load a shelf from an untrusted source. 
    Like with `pickle`, loading a shelf can execute arbitrary code.
    """

    
    try:
        with shelve.open(SHELVE_FILEPATH, writeback=False) as db:

            flag = table_key in db

            # TODO: autoremove *key* if the len(data) < len(db[table_key])
            if flag:
                # extract a copy
                _holder = db[table_key]
                # mutate the copy
                _holder.update(data)
                # stores the copy right back, to persist it
                db[table_key] = _holder                
            else:
                db[table_key] = data
    except Exception as msg:
        log.error(f'persist_data_in_shelve_error: {msg}')
        return False
    else:
        return True


def shelf_read(table_key: str, SHELVE_FILEPATH: str= SHELVE_FILEPATH):
    """Returns the dictionary stored at `table_key`

    :param table_key: table name used as key to store the dictionary.
    :param SHELVE_FILEPATH: filepath of the shelve file.

    :returns: if success returns {table_key: db[table_key]} else None
    """
    try:            
        with shelve.open(SHELVE_FILEPATH, writeback=False) as db:
            
            flag = table_key in db

            if flag:
                return {table_key: db[table_key]}
            else:
                return None
    except Exception as msg:
        log.error(f'shelf read error: {msg}')
        return None
        

def match_in_shelve(input: List[str], table_key: str = 'biota_columns') -> list:
    """Matches an input list of strings to the dictionary keys stored in `table_key`

    :param input: List of strings to match in `table_key` dictionary
    :param table_key: string name with the table key to search in shelf. 

    :returns: a list with the items from the input list found in `table_key`. 
              `None` if match was unsuccessfull
    """

    result = shelf_read(table_key)
    if result is not None:
        return [c for c in result[table_key] if c in input]
    else:
        return None


