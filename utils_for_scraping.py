#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 08-05-2015
Purpose:
#----------------------------------------------------------------
"""

import os
import sys
import getpass
import json
import shelve
from ConfigParser import ConfigParser

import installation_tasks


# NOTE TO SELF if letting the user manage their own login information, then ini files seem like the best way to go, but
# if storing that info ourselves (while gathering it from a command prompt, like what github does on the cmdline), then 
# something else (like json?) would be best since writing to ini files is not very clean (and erases all commments).

cookies_file = os.path.join(installation_tasks.config_dir, 'cookies.db')

def manage_cookies():
    cookies = shelve.open(cookies_file, writeback=True)
    return cookies

#cookies_file = os.path.join(installation_tasks.config_dir, 'cookies.json')

#def get_cookies():
    #if os.path.exists(cookies_file):
        ##with open(cookies_file, 'r') as f:
            ##cookies = json.load(f)
        #cookies = shelve.open(cookies_file, writeback=True)
    #else:
        #cookies = {}

    #return cookies

#def set_cookie(cookie_info):
    #with open(cookies_file, 'w') as f:
        #json.dump(cookie_info, f)



def get_user_credentials():
    ''' A ~/.configs/datalad/ dir should have been created to house stuff for our use.
    '''

    username = raw_input("Username: ")
    password = getpass.getpass()
    user_and_password = {'username': username, 'password': password}  

    # FIXME need to try out these values to see if it actually logs the user in or not; like give
    # them three chances to login before bailing or something like that.
    #assert len([v for v in user_and_password.values() if v]) == 2, "ERROR: need to enter correct value for both 'username' and 'password'"
    
    return user_and_password




#data_provider='crcns'
#def get_user_credentials(rcfile, data_provider=data_provider):
    #''' A ~/.configs/datalad/ dir should have been created to house stuff for our use.
    #'''


    #if hasattr(sys, 'real_prefix'):     # tests if in a virtual env
        ## see if .dataladrc exists in there, and if so, open it; if not,  
        ## ask for them on the commandline
        #pass
    #else:
        ## this will be in the user's home directory (should have been created during installation)
        #config_parser = ConfigParser()
        #config_parser.read(rcfile)
        #if config_parser.has_section(data_provider):
            #user_and_password = dict(config_parser.items(data_provider))
            #assert(sorted(user_and_password.keys()) == ['password', 'username'], 
                   #"ERROR: need 'username' and 'password' in {} for {}".format(rcfile, data_provider)) 
        #else:
            ## FIXME something like this to prompt the user for username and password (won't work with ini type file)            
            #username = raw_input("Username: ")
            #password = getpass.getpass()

            ##data_provider = 'someothersite'

            ##config_parser.add_section(data_provider)
            ##config_parser.set(data_provider, 'username', username)
            ##config_parser.set(data_provider, 'password', password)
            ##config_parser.write(rc)
            ##config_parser.close()
            ##rc.close()
            ##user_and_password = dict(config_parser.items(data_provider))
            #user_and_password = {'username': username, 'password': password}  

        ## FIXME need to try out these values to see if it actually logs the user in or not; like give
        ## them three chances to login before bailing or something like that.
        #assert(len([v for v in user_and_password.values() if v]) == 2, 
               #"ERROR: need to enter correct value for both 'username' and 'password'")
        
        #return user_and_password
