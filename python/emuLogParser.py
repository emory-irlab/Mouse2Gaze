'''
Created on Mar 20, 2012

@author: dlagun
'''

import utils
from BeautifulSoup import BeautifulSoup
import snippet_utils
from SearchSnippet import SearchSnippet 
_DEBUG_LEVEL = 0

class emuParser():
    def __init__(self, path):        
        self.log_path = path
        
        self.StudyBeginTime = 0
        
        self.StudyBeginEndTime = 0      
        
        # scroll events sorted by time 
        self.ScrollEvents = [] 
        
        # all tasks
        self.tasks = {} 
        
        # tasks sorted by time 
        self.task_order = []       
        
        # count of page ids
        self.page_id_cnt = 1
        
        # merged mouse movement events 
        self.mouse_merged = ""
        
        # merged gaze recordings
        self.gaze_merged = ""
            
        # result layout events indexed by page id
        self.result_layout = {}
        
        # result layout events indexed by page id
        self.contet_cache = {}
                
        # parse
        self.parse()
        
        # used to locate cached pages 
        self.content_cache_base_path = ""
                
        # stores snippet features, indexed page id
        self.search_results = {}
        
    # parses cached content and returns id of ten results 
    def parse_cached_page(self, path):                    
        soup = BeautifulSoup (open(path,"r"))        
        [search_results, result_cnt] = snippet_utils.parse_google_serp(soup)
        ret = []
        print "parsing " + path, " got %s results " % len(search_results) 
        #for result in search_results:
            # print result.res_id + "\t" + result.title
        #    ret.append(result.res_id)                            
        return search_results  
    
    # appends events to list             
    def append_events(self, events, line):
        params = utils.parse_emu_params(line)        
        if "http://ir-ub.mathcs.emory.edu/" in params['url']:
            params['query'] = user_study_queries[eval(params['task_idx'])]             
        elif "google.com/search" in params['url']:
            tmp = utils.parse_url_params(params['url'])                    
            params['query'] = tmp['q']                    
        if 'MouseOverOut' in line:
            return events
        tab_id = params['tab']
        wid = params['tab']        
        if params['ev'] =='MouseMove': # expands mousemove buffer 
            if params['is_doc_area'] == "1":
                points = params['buff'].split('|')                         
                for p in points:
                    tmp = p.split(',')
                    ret = {}
                    ret['ev'] = 'MouseMove'
                    ret['tab'] = tab_id  
                    ret['wid'] = wid
                    ret['time'] = eval(tmp[0]) 
                    ret['cx'] = eval(tmp[1])
                    ret['cy'] = eval(tmp[2])
                    ret['ax'] = eval(tmp[3]) + eval(tmp[1])
                    ret['ay'] = eval(tmp[4]) + eval(tmp[2])  
                    ret['xOffset'] = eval(tmp[3])
                    ret['yOffset'] = eval(tmp[4])                
                    ret['task_idx'] = params['task_idx']                              
                    ret['task_num'] = params['task_num']
                    ret['url'] = params['url']
                
                    events.append(ret)        
        elif params['ev'] =='Scroll': # expands scroll buffer             
            for p in params['buff'].split('|'):
                tmp = p.split(',')
                ret = {}
                ret['ev'] = 'Scroll'
                ret['tab'] = tab_id  
                ret['wid'] = wid
                ret['time'] = eval(tmp[0]) 
                ret['scrollLeft'] = eval(tmp[1])
                ret['scrollTop'] = eval(tmp[2])
                ret['xOffset'] = eval(tmp[3])
                ret['yOffset'] = eval(tmp[4])       
                ret['url'] = params['url']                
                ret['task_idx'] = params['task_idx']                              
                ret['task_num'] = params['task_num']
                                         
                events.append(ret)
                self.ScrollEvents.append(ret)
        elif params['ev'] =='TabSelect': # expands scroll buffer
            ret = {}
            ret['ev'] = 'TabSelect'
            ret['tab'] = tab_id  
            ret['wid'] = wid
            ret['time'] = eval(params['time']) 
            ret['xOffset'] = eval(params['offsetX'])
            ret['yOffset'] = eval(params['offsetY'])     
            ret['ref'] = params.get('ref', '')               
        elif params['ev'] =='PageShow': # expands scroll buffer
            ret = {}
            ret['ev'] = 'PageShow'
            ret['tab'] = tab_id  
            ret['wid'] = wid
            ret['time'] = eval(params['time']) 
            ret['xOffset'] = eval(params['offsetX'])
            ret['yOffset'] = eval(params['offsetY'])                      
        elif params['ev'] == 'resultLayout':
            params['time'] = eval(params['time'])                                
            idx = line.find("data=")
            if idx > 0:
                if idx + 6 > len(line):
                    params['data='] = ""
                else:                 
                    params['data'] = line[idx+6:]
            events.append(params)                
        elif params['ev'] == 'StudyBegin':
            self.StudyBeginTime = eval(params['time'])
            params['time'] = eval(params['time'])
            events.append(params)            
        elif params['ev'] == 'StudyEnd':
            self.StudyBeginEndTime = eval(params['time'])
            params['time'] = eval(params['time'])            
            events.append(params)
        elif params['ev'] == 'TaskFeedback':
            self.StudyBeginEndTime = eval(params['time'])
            params['time'] = eval(params['time'])            
            if params['success_val'] is '':
                params['success'] = -1
            else: params['success'] = eval(params['success_val'])
            if params['diff_val'] is '':
                params['difficulty'] = -1
            else: params['difficulty'] = eval(params['diff_val'])            
            events.append(params)
        elif params['ev'] == 'RelevanceLabel':
            self.StudyBeginEndTime = eval(params['time'])
            params['time'] = eval(params['time'])            
            if params['rel_val'] == 'ignore':
                params['relevance'] = -1
            else: params['relevance'] = eval(params['rel_val'])
            events.append(params)                               
        else:
            params['time'] = eval(params['time']) 
            events.append(params)                
        return events
    
    # parse events 
    
    def parse(self):        
        f = open(self.log_path, 'r')
        events = []
        line_cnt = 0
        for l in f:            
            l = l.rstrip("\r\n").replace("192.168.0.1 - - [01/Jan/2010:00:00:00 -0500] \"GET /v=EMU.0.8&","")            
            events = self.append_events(events, l)
            line_cnt +=1
        
        if _DEBUG_LEVEL > 0:
            print "processed %s events " % len(events)
        
        # sort 
        self.events = sorted(events, key=lambda x: x['time'], reverse=False)
        tmp = self.ScrollEvents 
        self.ScrollEvents = sorted(tmp, key=lambda x: x['time'], reverse=False)
        
        # split tasks 
        for e in self.events:           
            if  e.has_key('task_idx') and eval(e['task_num']) > 0:
                if not self.tasks.has_key(e['task_idx']):
                    self.tasks[e['task_idx']] = []
                    self.task_order.append(e['task_idx'])
                self.tasks[e['task_idx']].append(e)                                                        
        
        self.task_pages = {}
        for t in self.task_order:            
            self.task_pages[t] = self.segment_pages(self.tasks[t][:])
            for e in self.tasks[t]:
                if e['ev'] == 'resultLayout':                
                    self.result_layout[e['pid']] = e                                            
                if e['ev'] == 'contentCache':                
                    self.contet_cache[e['pid']] = e
        
        #for pid in self.result_layout:    
        #    print pid, self.result_layout[pid]                           
                                                                    
        if _DEBUG_LEVEL > 0:
            o = open('C:\\lagoon\\workspace\\m2g\\log\\events.tmp','w')    
            for e in self.tasks['2']:
                o.write("%s \t %s \t %s\n" % (e['time'], e['ev'], e['url']))                
            o.close()
                
            events = self.tasks['2']
            for page in self.task_pages['2']:
                print page.url                
                for s in page.slices:
                    b = events[s['beg']]
                    e =  events[s['end']]
                    print b['ev'], b['time'] , " --> ", e['ev'],e['time']
            
    # parse result pages 
    def parse_serps(self):
        for pid in self.result_layout:            
            self.search_results[pid] = self.get_search_results(pid)                                       
    
    # parse search results 
    def get_search_results(self, pid):        
        search_results = []
        resultLayout = self.result_layout[pid]
        contentCache = self.contet_cache[pid]
        
        is_serp = 1 if "google.com/search" in contentCache['url'] or "ir-ub.mathcs.emory.edu/intent/user-study/tasks/" in contentCache['url'] else 0
        # print pid, "\t", is_serp, "\t", contentCache['url'], 
        if is_serp == 0:
            return search_results
        
        # if cached page was scrolled                
        """ 
        ret = str(self.user_id) + "\t" + str(resultLayout['pid'])
        ret += "\t" + str(contentCache['scrlW'])
        ret += "\t" + str(contentCache['scrlH'])
        ret += "\t" + str(contentCache['offsetX'])
        ret += "\t" + str(contentCache['offsetY'])        
        ret += "\t" + str(contentCache['iw'])
        ret += "\t" + str(contentCache['ih'])
        """        
        data = resultLayout.get('data', "")
        data = data.replace(" ","")                    
        query_string = resultLayout['query'] 
        if data is None or len(data) < 10:
            search_results  = []            
        else:
            results_layout = utils.parse_result_layout_data(data)                        
            results_html = self.parse_cached_page(self.content_cache_base_path + resultLayout['content_id'] + ".html")            
            for i in range(0, len(results_html)):                
                id = results_html[i].res_id
                results_layout[id]['x0'] = eval(results_layout[id]['x0']) + eval(contentCache['offsetX'])
                results_layout[id]['y0'] = eval(results_layout[id]['y0']) + eval(contentCache['offsetY'])                                             
                search_results.append(SearchSnippet(results_html[i].url, results_html[i].title, results_html[i].snip_body, 
                                                    results_html[i].snip_html, results_html[i].title_html,
                                                    results_html[i].res_pos, results_html[i].res_id, 
                                                    results_layout[id], resultLayout['content_id'],  
                                                    query_string, resultLayout['url']))                                               
        return search_results
                
    # filter feedback dialogs
    def segment_pages(self, events):                                    
        slices = []
        n_slices = 0        
        i = 0
        pages = []
        beg = -1              
        for e in events:
            e['pid'] = self.page_id_cnt                                       
            if e['ev'] == 'LocationChange1':
                if beg > 0:
                    tmp = {}
                    tmp['beg'] = beg
                    tmp['end'] = i - 1
                    if i > beg:
                        slices.append(tmp)
                        n_slices += 1
                    if n_slices > 0:                                    
                        pages.append(emuPage(slices, self.page_id_cnt, events[slices[0]['beg']]))
                        slices = []
                        n_slices = 0                                                        
                        self.page_id_cnt += 1
                beg = i                                        
            if e['ev'] == 'FeedbackDialogOpen' and beg > 0:
                tmp = {}
                tmp['beg'] = beg
                tmp['end'] = i - 1               
                if beg < i :
                    slices.append(tmp)                                        
                    n_slices += 1
                beg = -1
            if e['ev'] == 'FeedbackDialogClose':
                beg = i + 1
            if e['ev'] == 'PostTaskQuestionOpen' and beg > 0:
                tmp = {}
                tmp['beg'] = beg
                tmp['end'] = i - 1
                if beg < i:
                    slices.append(tmp)
                    n_slices += 1
                beg = -1
            if e['ev'] == 'PostTaskQuestionClose':
                beg = i + 1            
            i = i + 1
                                                                    
        return pages                                                   
        
class emuPage():    
    def __init__(self, slices, pid, e, prev_page_id = -1):
        self.slices = slices      
        self.page_id = pid
        self.url = e['url']
        self.emu_event_slices = []
        self.gaze_fix_slices = []
        self.pageEvent = e
        self.pageCacgeEvenet = None        
        self.pageLoadTime = e['time']
        self.prev_page_id = -1
        # debug
        #print self.pageEvent['time'], self.url
                
        
# example file  
#parser = emuParser()
#parser.parse('C:\\Data\\Cache\\panel1332277229476.dat')
#print "detected %s pages" % len(parser.pages)
user_study_queries = {}
user_study_queries[0] = "best selling book 2011 US"
user_study_queries[1] = "average temperature Dallas, SD"
user_study_queries[2] = "2011 airplane crash US"
user_study_queries[3] = "US worst drought"
user_study_queries[4] = "how many dead pixels ipad 3 replace"
user_study_queries[5] = "State Radio Atlanta"
user_study_queries[6] = "Target Emory"
user_study_queries[7] = "Dow Jones Industrial Average"
user_study_queries[8] = "Comcast Emory"
user_study_queries[9] = "vegetarian restaurants Lenox Square"
user_study_queries[10] = "bank of america number gatech"
user_study_queries[11] = "car inspection decatur, GA"



