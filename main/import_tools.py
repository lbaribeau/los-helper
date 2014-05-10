import os, sys, inspect

def import_subdir(subdir):
    # use this if you want to include modules from a subforder
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],subdir)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)