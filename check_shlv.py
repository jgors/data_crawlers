#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 07-13-2015
Purpose:
#----------------------------------------------------------------
"""

import shelve
s = shelve.open('./crcns.shlv')
print "All dataset keys:"
print sorted(s.keys())
print len(s.keys())


data_sets = s['Data Sets']
print data_sets.keys()
vc = data_sets['Visual cortex']
print vc

s.close()
