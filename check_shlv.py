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
#print vc
vc

s.close()

for section, section_datasets in data_sets.items():
    for dataset, content in section_datasets.items():
        #print dataset, content
        print dataset
        for k, v in content.items():
            if k.startswith('About '):
                print '  '+'\n  '.join(v['h2s']) 
