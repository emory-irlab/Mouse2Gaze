'''
Created on Mar 20, 2012

@author: dlagun
'''
import re, sys, os
import datetime, time
class tobiiFixationParser():
    def __init__(self, path):
        self.fixations = []
        self.slices = []
        
        # load fixations
        f = open(path, 'r')
        ignore_flag = True
        rec_date = []
        rec_time = ""
        for l in f:            
            if 'Recording date' in l:
                rec_date = self.arrayStr2arrayInt(l.replace("Recording date: ","").rstrip().split('/'))
            if 'Recording time' in l:
                rec_time = self.arrayStr2arrayInt(l.replace("Recording time: ","").replace(" (corresponds to time 0)", "").rstrip().split(':'))
                self.rec_time = rec_time
                self.start_ts = datetime.datetime(rec_date[2], rec_date[0], rec_date[1], rec_time[0], rec_time[1], rec_time[2], 1000*rec_time[3])
                self.start_ts_milli = (1000*int(time.mktime(self.start_ts.timetuple())) + self.rec_time[3])                                                   
                      
            if ignore_flag is False: # parse data
                s = l.rstrip().split('\t')                
                tmp = {}
                tmp['FixationIndex'] = eval(s[0])
                tmp['Timestamp'] = self.start_ts_milli + eval(s[1])
                tmp['FixationDuration'] = eval(s[2])
                tmp['x'] = eval(s[3])
                tmp['y'] = eval(s[4])
                self.fixations.append(tmp)
            if 'FixationIndex' in l: 
                ignore_flag = False                        
           
    def arrayStr2arrayInt(self, arg):
        ret = []
        for v in arg:
            ret.append(eval(v))
        return ret    
    
    # returns fixations for specified interval     
    def getSlice(self, start_ts, end_ts):
        fslice = []                
        for f in self.fixations:             
            if f['Timestamp'] >= start_ts:
                fslice.append(f)
            if f['Timestamp'] > end_ts:
                break         
        return fslice
#fix_parser = tobiiFixationParser('C:\\lagoon\\workspace\\m2g\\eye-tracking\\P6\\Rec 06-Fixation-Data.tsv')