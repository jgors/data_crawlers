#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 08-05-2015
Purpose:
#----------------------------------------------------------------
"""


import os

# to get where app configs live on the system (to store data providers cookies/session info)
from xdg.BaseDirectory import xdg_config_home


proj_name = 'datalad'   # TODO this is just for now, but will be defined better later

config_dir = os.path.join(xdg_config_home, proj_name) 
if not os.path.exists(config_dir):
    os.makedirs(config_dir) 

# this could be for storing the username and password info
#usr_home = os.path.expanduser("~")
#rcfile = os.path.join(usr_home, ".{}rc".format(proj_name))

#if not os.path.exists(rcfile):
    #with open(rcfile, 'w') as f:
        #s = '# File used to store credentials for data providers, like so:' 
        #s += "\n\n#[sitename]\n#username: myusername\n#password: mypassword\n"
        #f.write(s)
