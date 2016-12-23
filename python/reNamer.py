'''
Created on Apr 19, 2012

@author: dlagun
'''
import sys, os
import shutil
path = 'C:\\lagoon\\Data\\User-Study-m2g\\Tobii-Structured\\'
for filename in os.listdir(path):
    print filename
    for fn in os.listdir(path + filename):
        print "\t", path + filename + "\\" + fn, "-->", "All-Data"
        if 'All-Data' in fn:
            os.rename(path + filename + "\\" + fn, path + filename + "\\" + "All-Data.tsv")
        if 'Fixation-Data' in fn:
            os.rename(path + filename + "\\" + fn, path + filename + "\\" + "Fixation-Data.tsv")