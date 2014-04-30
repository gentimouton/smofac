import ConfigParser
import logging
import os

# game mechanics and graphics config
_logger = logging.getLogger('smofac')
_dic = {} # store pairs of (config option, value)
config_filepath = "smofac.conf"
config = ConfigParser.ConfigParser()
fp = os.path.abspath(config_filepath)
files_read = config.read(fp)

if not files_read: #config.read() could not find the config file
    _logger.critical('Could not find config file at %s' % os.path.abspath(fp))
    exit()

for section in config.sections():
    options = config.options(section)
    for option in options:
        try:
            _dic[option] = config.get(section, option)
        except:
            _dic[option] = None
            _logger.error('Exception on option %s' % option)

# _dic now contains all the config variables; let's expose them!


def int_tuple(str_):
    """ Transform a string of integers into a tuple.
    Example: '1,2,3' becomes (1,2,3)
    """
    strlist = str_.strip().split(',') # ['1','2','3']
    return tuple([int(i) for i in strlist]) #tuple of int: (1,2,3)


# gfx
fps = float(_dic['fps'])
steps_per_cell = int(_dic['steps_per_cell'])
cell_size = int(_dic['cell_size'])
resolution = int_tuple(_dic['resolution'])
font_size = int(_dic['font_size'])

bg_color = int_tuple(_dic['bg_color'])
trap_color = int_tuple(_dic['trap_color'])
path_color = int_tuple(_dic['path_color'])
blender_color = int_tuple(_dic['blender_color'])


_logger.info('Loaded config')
