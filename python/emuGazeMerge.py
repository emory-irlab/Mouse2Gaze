'''
Created on Mar 20, 2012

@author: dlagun
'''
import tobiiFixationParser
import emuLogParser
import tobiiRawDataParser
import math
import utils
from pylab import *

_PARSE_SERPS = True
_GAZE_Y_OFFSET = 93 # px

class emuGazeMerger():        
        
    def __init__(self,gaze_data_path, emu_data_path, user_id = 0, start_page_id = 0, log_directory = ""):
        self._DEBUG_LEVEL = 0
        self.user_id = user_id        
        self.emuLog = emuLogParser.emuParser(emu_data_path)      
        self.emuLog.content_cache_base_path = log_directory
        if _PARSE_SERPS:
            self.emuLog.parse_serps()          
        self.task_id = 0
        self.task_start_time = 0
        self.page_start_time = 0
        self.log_directory = log_directory      
        self.db_export = []          
        
        # for fixation data 
        #self.gazeLog = tobiiFixationParser.tobiiFixationParser(gaze_data_path)
        
        # for raw data
        self.gazeLog = tobiiRawDataParser.tobiiRawDataParser(gaze_data_path)
        
        self.mouse_merged = ""
        self.gaze_merged = ""
        # self.page_contents = ""
                
        # merge
        for t in self.emuLog.task_order:            
            events = self.emuLog.tasks[t]
            for i in range(0, len(self.emuLog.task_pages[t])):
                self.task_id = t
                page = self.emuLog.task_pages[t][i]
                self.pg_id = page.page_id
                print "pid : %s \t url: %s" % (self.pg_id, page.url)                                                
                for i in range(0, len(page.slices)):                    
                    s = page.slices[i]
                    b = events[s['beg']] # begin 
                    e =  events[s['end']] # end                                                    
                    page.emu_event_slices.append(events[s['beg']:s['end']])       
                    slice_gaze_data = self.merge_slices(page, events[s['beg']:s['end']],
                                                             self.gazeLog.getSlice(b['time'], e['time']))   
                    page.gaze_fix_slices.append(slice_gaze_data)
                self.append_merged_data(slice_gaze_data, events[s['beg']:s['end']], page)
                self.emuLog.task_pages[t][i] = page
                                                              
    # prints out data in matrix format     
    def append_merged_data(self, gaze_data, emu_data, page):
        
        is_serp = 1 if "google.com/search" in page.url or "http://ir-ub.mathcs.emory.edu/intent/user-study/tasks/" in page.url else 0        
        # gaze 
        for f in gaze_data:
            seq = [self.user_id, 
                   self.task_id, 
                   self.pg_id, 
                   is_serp,
                   f['Timestamp'], 
                   f['Timestamp'] - self.emuLog.StudyBeginTime, 
                   f['cx'],
                   f['cy'] - _GAZE_Y_OFFSET,                   
                   f['offsetX'],
                   f['offsetY'],
                   f['pupilLeft'],
                   f['pupilRight']
                   ]
            
            
            self.db_export.append([self.user_id, 
                   self.task_id, 
                   self.pg_id, 
                   is_serp,                    
                   datetime.datetime.fromtimestamp(f['Timestamp']  / 1000.0),
                   f['Timestamp'] - self.emuLog.StudyBeginTime, 
                   f['cx'],
                   f['cy'] - _GAZE_Y_OFFSET,                   
                   f['offsetX'],
                   f['offsetY'],
                   f['pupilLeft'],
                   f['pupilRight']
                   ]
)
            self.gaze_merged += "\t".join(map(str, seq)) + "\n" 
        
        # mouse
        last_move_ts = -1                        
        for e in emu_data:
            if e['ev'] == 'MouseMove':
                tm = 1  
                [offsetX, offsetY, scrollEvent] = self.get_scroll_offset(page, e['time'])
                if last_move_ts > 0:
                    tm = e['time'] - last_move_ts                                    
                seq = [self.user_id, 
                       self.task_id, 
                       self.pg_id, 
                       is_serp,
                       e['time'], 
                       e['time'] - self.emuLog.StudyBeginTime, 
                       e['time'] - page.pageLoadTime + 1, 
                       tm, 
                       e['cx'], 
                       e['cy'],
                       offsetX,
                       offsetY]                                            
                self.mouse_merged += "\t".join(map(str, seq)) + "\n"
                last_move_ts = e['time']                                           
                                                  
    # plots {x,y} time - series
    def plot_mouse_trace(self, x, y, dur, title):
        f = figure('')    
        plt.plot(x,y,'-ro', alpha = 0.2)
        for i in range(1,len(x)):                        
            plt.plot(x[i], y[i], '-ro', alpha=0.2, markersize= dur[i] * 1e-4)                            
            plt.xlim((0, max(1400, max(x)) ))
            plt.ylim((0, max(1600, max(y)) ))                    
            ax = plt.gca()
            ax.set_ylim(ax.get_ylim()[::-1])    
            f.show()   
    
    # returns scroll offset for given ts                                                                                                                            
    def get_scroll_offset(self, page, ts):                
        offsetX = 0 
        offsetY = 0                
        scrollEvent = None
        for e in self.emuLog.ScrollEvents:                                     
            if e['tab'] == page.pageEvent['tab'] and e['url'] == page.pageEvent['url']:
                if e['time'] > ts:
                    break            
                else:
                    offsetX = (e['xOffset'])
                    offsetY = (e['yOffset'])
                    scrollEvent = e                          
        #if e['tab'] == 'panel13327921273321':
        #    print [offsetX, offsetY]                 
        return [offsetX, offsetY, scrollEvent]        
                          
    # merge slices                                      
    def merge_slices(self, page, emu, gaze):        
        fixations = []                                 
        if emu is not []:                                                    
            for fix in gaze:                
                [offsetX, offsetY, scrollEvent] = self.get_scroll_offset(page, fix['Timestamp'])                
                tmp = fix
                tmp['cx'] = fix['x']
                tmp['cy'] = fix['y']                                     
                tmp['offsetX'] = offsetX
                tmp['offsetY'] = offsetY                                            
                fixations.append(tmp)                                                              
        return fixations            
                                                                                                     