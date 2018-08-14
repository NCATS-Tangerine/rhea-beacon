import json

import os, yaml, threading
from datetime import date, timedelta

__config_dict = None

def snake_case(string):
    return string.lower().replace(' ', '_')

def map_category(category):
    """
    Monarch's categories don't perfectly map onto the biolink model
    https://github.com/biolink/biolink-model/issues/62
    """
    return {
        'variant' : 'sequence variant',
        'phenotype' : 'phenotypic feature',
        'sequence variant' : 'variant',
        'phenotypic feature' : 'phenotype',
        # 'model' : 'model to disease mixin'
    }.get(category.lower(), category)

def base_path_search():
    return 'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2?q='

def base_path_reaction():
    return 'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2/'

def check_status(response):
    """
    Throws an exception if response code is not 200
    """
    if response.status_code != 200:
        raise Exception(response.url + " returned status code: " + str(response.status_code))

def biolink_prefix():
    """
    Biolink associations do not generally follow the curie syntax. In such cases
    the resulting statement curie identifier will be set as:

    biolink_prefix() + ':' + biolink_association_id
    """
    return 'biolink'

def get_property(d, key, default_value=None):
    """
    Exhausts each affix before returning default value.

    Parameters
    ----------
    d : dict
        representing a monarch bioentity
    key : str
        the key of the property to be obtained
    """
    affixes = ['_eng', '_std', '_kw']
    try:
        return d[key]
    except:
        for affix in affixes:
            try:
                return d[key + affix]
            except:
                pass
    return default_value

def sanitize_str(s):
    """
    Ensures that s is a string. If it's a list or tuple then it joins the items
    into a string deliminated by a space.
    """
    if isinstance(s, (list, tuple, set)):
        return ', '.join([sanitize_str(x) for x in s])
    else:
        return s

def sanitize_int(i, default_value=1):
    """
    Ensures that i is a positive integer
    """
    return i if isinstance(i, int) and i > 0 else default_value

def try_multi(method, repeats=5, **kwargs):
    """
    Will attempt to call method a number of times, returning the
    results if successful.
    """
    for i in range(repeats):
        try:
            return method(**kwargs)
        except Exception as e:
            pass

    raise Exception('Tried to call ' + method.__name__ + ' ' + repeats + ' many times and failed')

def load_config(silent=True):
    """
    Walks backwards from __file__ to find config.yaml, loads and returns as a
    dictionary.

    Note: traverses up whole file system if config.yaml is not found, but this
          doesn't appear to be a costly opperation.

    source: https://www.programcreek.com/python/example/3198/yaml.safe_load
    """

    global __config_dict

    if __config_dict is not None:
        return __config_dict

    config = None
    f = __file__
    while config is None:
        d = os.path.dirname(f)
        path = os.path.join(d, 'config.yaml')

        if not silent:
            print('Searching for config.yaml in:', path)

        if os.path.isfile(path):
            config = path
            break
        elif f == d:
            break

        f = d

    if not config:
        raise Exception('Could not find config.yaml in any parent directory of {}, try copying and renaming {} in projects root directory'.format(__file__, __sample_name))

    __config_dict = yaml.safe_load(open(config).read())

    return __config_dict