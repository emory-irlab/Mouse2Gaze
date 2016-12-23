'''
Created on Mar 21, 2012

@author: dlagun
'''
import re, sys, os
import datetime, time
class tobiiRawDataParser():
    def __init__(self, path):
        self.fixations = []
        self.slices = []
        
        # load fixations
        f = open(path, 'r')
        ignore_flag = True
        self.rec_date = []        
        data_fields = {}
        for l in f:            
            if 'Recording date' in l:
                self.rec_date = self.arrayStr2arrayInt(l.replace("Recording date:\t ","").rstrip().split('/'))
            #if 'Recording time' in l:
            #    rec_time = self.arrayStr2arrayInt(l.replace("Recording time: ","").replace(" (corresponds to time 0)", "").rstrip().split(':'))
            #    self.rec_time = rec_time
            #    self.start_ts = datetime.datetime(rec_date[2], rec_date[0], rec_date[1], rec_time[0], rec_time[1], rec_time[2], 1000*rec_time[3])
            #    self.start_ts_milli = (1000*int(time.mktime(self.start_ts.timetuple())) + self.rec_time[3])                                                   
            
            s = l.rstrip().split('\t')                  
            if ignore_flag is False and len(s) > 30: # parse data                            
                tmp = {}                                
                #tmp['FixationIndex'] = eval(s[0])
                #tmp['Timestamp'] = self.start_ts_milli + eval(s[data_fields['Timestamp']])
                tmp['Timestamp'] = self.str2milliseconds(s[data_fields['DateTimeStamp']])                
                #tmp['Timestamp'] = eval(s[data_fields['AbsoluteMicroSecondTimestamp']])                
                tmp['FixationDuration'] = 1000 / 60.0 # 60 Hz                
                tmp['x'] = eval(s[data_fields['GazePointX']])
                tmp['y'] = eval(s[data_fields['GazePointY']])
                tmp['pupilLeft'] = eval(s[data_fields['PupilLeft']])
                tmp['pupilRight'] = eval(s[data_fields['PupilRight']])                
                tmp['ValidityLeft'] = eval(s[data_fields['ValidityLeft']])
                tmp['ValidityRight'] = eval(s[data_fields['ValidityRight']])                
                if tmp['ValidityRight'] == 0 and tmp['ValidityLeft'] == 0 and tmp['x'] > 0 and tmp['y'] > 0: 
                    self.fixations.append(tmp)                
            if 'Timestamp' in l: 
                ignore_flag = False                
                i = 0
                for f in l.split("\t"):
                    data_fields[f] = i                    
                    i += 1                
    
    # converts DateTimeStamp to milliseconds 
    def str2milliseconds(self, str):        
        rec_time = self.arrayStr2arrayInt(str.replace(".",":").split(':'))
        ts = datetime.datetime(self.rec_date[2], self.rec_date[0], self.rec_date[1], rec_time[0], rec_time[1], rec_time[2], 1000*rec_time[3])
        return (1000*int(time.mktime(ts.timetuple())) + rec_time[3])                                                      
    
    # converts array to string       
    def arrayStr2arrayInt(self, arg):
        ret = []
        for v in arg:
            v = re.sub(r"^0+","",v)
            if v is not "":                        
                ret.append(eval(v))
            else: ret.append(0)            
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
#fix_parser = tobiiRawDataParser('C:\\lagoon\\workspace\\m2g\\eye-tracking\\P9\\Rec 07-All-Data.tsv')
#print len(fix_parser.fixations)