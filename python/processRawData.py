'''
Created on Apr 19, 2012

@author: dlagun
'''
from scipy.stats.stats import pearsonr
import os, sys, datetime
import emuGazeMerge
import sys, psycopg2,psycopg2.extras
import numpy

_DUMP_EVENTS_TO_DB = True

db_connect = "dbname='m2g' user='dlagun' password='lagoon12345' host='localhost'"

tobii_path = "C:\\lagoon\\Data\\User-Study-m2g\\Tobii-Structured\\"
emu_path = "C:\\lagoon\\Data\\User-Study-m2g\\EMU-Structured-Valid\\"

mouse_out = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\mouse_out'
gaze_out = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\gaze_out'
page_content_out = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\content_out'
page_relevance_out = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\relevance_out'
task_feedback_out = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\task_out'

def process_log_data():
    mf = open(mouse_out, 'w+')
    gf = open(gaze_out, 'w+')
    pc = open(page_content_out, 'w+')
    
    conn = None
    cur = None

    if _DUMP_EVENTS_TO_DB is True:
        conn = psycopg2.connect(db_connect)    
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        ################# EMU EVENTS TABLE #############################
        try : 
            cur.execute("DROP TABLE emu_events")        
        except: pass
        conn.commit()
        sql = """ CREATE TABLE emu_events(          ev_id bigint,
                                                    user_id integer,                                                    
                                                    task_idx integer,
                                                    task_num integer,
                                                    tab_id varchar(128),
                                                    wid varchar(128),
                                                    ts timestamp,
                                                    microseconds bigint,
                                                    page_id integer,
                                                    event_name varchar(128),  
                                                    url text,       
                                                    ref text,                                                             
                                                    event_data text,
                                                    cx integer,
                                                    cy integer,
                                                    offsetX integer,
                                                    offsetY integer,
                                                    success integer,
                                                    difficulty integer,
                                                    relevance integer)                                                                                        
                                              """
        cur.execute(sql)
        conn.commit()
        
        ################# SEARCH RESULT TABLE #############################
        try : 
            cur.execute("DROP TABLE search_results ")        
        except: pass
        conn.commit()
        sql = """ CREATE TABLE search_results(      user_id integer,                                                    
                                                    page_id integer, 
                                                    rank integer, 
                                                    url text,
                                                    serp_url text,
                                                    query_string text,
                                                    x0 integer,
                                                    cw integer,
                                                    y0 integer,
                                                    ch integer
                                                    )                                                                                        
                                              """
        cur.execute(sql)
        conn.commit()
                
        ################# GAZE DATA #############################
        
        try : 
            cur.execute("DROP TABLE gaze_data ")        
        except: pass
        conn.commit()
        sql = """ CREATE TABLE gaze_data (          user_id integer,                                                    
                                                    task_id integer, 
                                                    page_id integer,
                                                    is_serp integer,                                                 
                                                    ts timestamp,
                                                    time_since_study_begin integer,
                                                    ax integer,
                                                    ay integer,
                                                    offsetX integer,
                                                    offsetY integer,
                                                    pupilLeft real,
                                                    pupilRight real                                                    
                                                    )                                                                                        
                                              """
        cur.execute(sql)
        conn.commit()
        
        ##################### RESULT READING DATA #####################
        
        try : 
            cur.execute("DROP TABLE gaze_result_examination ")        
        except: pass
        conn.commit()
        sql = """ CREATE TABLE gaze_result_examination (    user_id integer,                                                                                                        
                                                            page_id integer,            
                                                            ts timestamp,                                                                                         
                                                            time_since_page_load integer,
                                                            result_pos integer                                                    
                                                    )                                                                                        
                                              """
        cur.execute(sql)
        conn.commit()
        
    sql_insert_event = "INSERT INTO emu_events (ev_id, user_id, task_idx, task_num, tab_id, wid, ts, microseconds, page_id, event_name, url, ref, event_data, cx, cy, offsetX, offsetY, success, difficulty, relevance)"
    sql_insert_event += " VALUES (" + ", ".join(["%s"]*20) + ")"
    
    sql_insert_search_result = "INSERT INTO search_results (user_id, page_id, rank, url, serp_url, query_string, x0, cw, y0, ch) "
    sql_insert_search_result += " VALUES (" + ", ".join(["%s"]*10) + ")"
    
    sql_insert_gaze_data = "INSERT INTO gaze_data (user_id, task_id, page_id, is_serp, ts, time_since_study_begin, ax, ay, offsetX, offsetY, pupilLeft, pupilRight)"
    sql_insert_gaze_data += " VALUES (" + ", ".join(["%s"]*12) + ")"
    
    sql_insert_result_examination_sequence = "INSERT INTO gaze_result_examination (user_id, page_id, ts, time_since_page_load, result_pos)"
    sql_insert_result_examination_sequence += " VALUES (" + ", ".join(["%s"]*5) + ")"
    
    ev_id = 0
    for filename in os.listdir(tobii_path):
        print filename
        merger = emuGazeMerge.emuGazeMerger(tobii_path + filename + "\\All-Data.tsv", emu_path + filename + "\\EMU_LOG.dat", eval(filename.replace("P","")), 0,     emu_path + filename + "\\")    
        mf.write(merger.mouse_merged)
        gf.write(merger.gaze_merged)                
        pc.write(get_result_string(merger.user_id, merger.emuLog.search_results))
        
        merger.mouse_merged = ""
        merger.gaze_merged=  ""        
            
        # insert emu events into DB if needed 
        if _DUMP_EVENTS_TO_DB is True:
            ############################# DUMP EVENTS ###########################################
            batch = []
            for t in merger.emuLog.tasks:
                for e in merger.emuLog.tasks[t]:                                  
                    batch.append([ev_id, eval(filename.replace("P","")), e['task_idx'], e['task_num'],
                                   e['tab'], e['wid'], datetime.datetime.fromtimestamp(e['time']  / 1000.0), e['time'], e.get('pid',-1), 
                                   e['ev'], e['url'], e.get('ref',''), '', 
                                   e.get('cx',0), e.get('cy',0), e.get('xOffset',0), e.get('yOffset',0), e.get('success',-1), e.get('difficulty',-1), e.get('relevance',-1) ])
                    ev_id += 1
            cur.executemany(sql_insert_event, batch)
            conn.commit()
            
            ############################# DUMP SEARCH RESULTS ##################################
            batch = []
            for page_id in merger.emuLog.search_results:
                for result in merger.emuLog.search_results[page_id]:
                    batch.append([merger.user_id, page_id, result.res_pos, result.url, result.serp_url, result.query_string, 
                                  result.x0, result.cw, result.y0, result.ch])
            cur.executemany(sql_insert_search_result, batch)
            conn.commit()
            
            ############################# GAZE MOVEMENTS ##################################                        
            
            cur.executemany(sql_insert_gaze_data, merger.db_export)
            conn.commit()
            
            ############################# GAZE MOVEMENTS ##################################
            
            cur.executemany(sql_insert_result_examination_sequence, get_result_examination_sequence(merger.user_id))
            conn.commit()
                                  
    mf.close()
    gf.close()
    pc.close()

def get_result_from_point(x, y, offsetY, results):
    res = -1 
    err = 5 # px             
    for i in range(0, len(results)):
        bottom_y = 844 + offsetY
        if x > results[i]['x0'] - err and x < results[i]['x0'] + results[i]['cw'] + err  and \
                                y > results[i]['y0'] - err and y < results[i]['y0'] + results[i]['ch'] + err and \
                                y < bottom_y  + err and y > offsetY - err:           
            res = results[i]['rank']
            # print x,"\t",y,"\t",res
            break
    return res
 
def get_result_examination_sequence(user_id):
    batch = []
    conn = psycopg2.connect(db_connect)    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur_res = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT distinct page_id FROM gaze_data WHERE is_serp = 1 and user_id = %s " % user_id)
    
    page_ids = (p for p in cur.fetchall())
    
    for pid in page_ids:
        cur_res.execute("SELECT * FROM search_results WHERE user_id = %s and page_id = %s " % (user_id, pid[0]))        
        results = []
        for res in cur_res.fetchall():
            tmp = {}
            tmp['x0'] = res['x0']
            tmp['cw'] = res['cw']
            tmp['y0'] = res['cw']
            tmp['ch'] = res['cw']
            tmp['rank'] = res['rank']
            results.append(tmp)
        if len(results) > 8:
            cur.execute("SELECT * FROM gaze_data WHERE user_id = %s and page_id = %s order by ts" % (user_id, pid[0]))
            first_flag = True        
            for e in cur.fetchall():                
                if first_flag:
                    first_flag = False
                    first_ts = e['ts']
                td = e['ts'] - first_ts
                res = get_result_from_point(e['ax'], e['ay'], e['offsety'], results)
                batch.append([user_id, pid[0], e['ts'], int(td.seconds*1000 + round(td.microseconds / 1000.0)), res])
    #for x in batch:
    #    print x
    return batch                             

def dump_relevance_data(path):    
    conn = psycopg2.connect(db_connect)    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    out = open(path,"w")    
    
    cur.execute("SELECT distinct user_id FROM emu_events")    
    users = []
    for v in cur.fetchall():         
        users.append(v[0])         
    for uid in users:         
        cur.execute("SELECT * from emu_events WHERE event_name = 'RelevanceLabel' and user_id = %s ORDER BY ts" % uid)
        pages = {}
        for row in cur.fetchall():
            if not pages.has_key(row['url']):
                out.write("%s\t%s\t%s\t%s\t%s\n" % (uid, row['task_num'], row['task_idx'], row['page_id'], row['relevance']))
                pages[row['url']] = 1                        
    out.close()     
    
def dump_feedback_data(path):
    conn = psycopg2.connect(db_connect)    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    out = open(path,"w")
               
    cur.execute("SELECT distinct user_id FROM emu_events")    
    users = []
    for v in cur.fetchall():         
        users.append(v[0])         
    for uid in users:         
        cur.execute("SELECT * from emu_events WHERE event_name = 'TaskFeedback' and user_id = %s ORDER BY ts" % uid)
        pages = {}
        for row in cur.fetchall():
            if not pages.has_key(row['url']):
                out.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (uid, row['task_num'], row['task_idx'], row['page_id'], row['success'], row['difficulty'] ))
                pages[row['url']] = 1                        
    out.close()     
                      
def get_result_string(uid, search_result):
    ret = ""
    for pid in search_result:
        for result in search_result[pid]:
            ret += str(uid) + "\t" + str(pid)
            ret += "\t" + str(result.x0) + "\t" + str(result.cw) + "\t" + str(result.y0) + "\t" + str(result.ch) + "\t"
            features = [result.title_length_words, 
                        result.title_length_char, 
                        result.title_frac_sw,
                        result.title_num_fragments,
                        result.title_num_cap,
                        result.title_num_punct,
                        result.title_num_digit,
                        result.title_num_cap_per_word,
                        result.title_num_cap_per_fragment,
                        result.title_avg_fragment_length,
                        result.title_num_mathces,                        
                        result.title_lenght_bolded_words,
                        result.title_lenght_bolded_chars,
                        result.title_frac_bolded,
                        result.snip_body_length_words,
                        result.snip_body_length_char,
                        result.snip_body_frac_sw,
                        result.snip_body_num_fragments,
                        result.snip_body_num_cap,
                        result.snip_body_num_punct,
                        result.snip_body_num_digit,
                        result.snip_body_length_words,
                        result.snip_body_num_cap_per_word,
                        result.snip_body_num_cap_per_fragment,
                        result.snip_body_avg_fragment_length,
                        result.snip_body_num_mathces,
                        result.snip_body_lenght_bolded_words,
                        result.snip_body_lenght_bolded_chars,
                        result.snip_body_frac_bolded,
                        result.url_num_cap,
                        result.url_num_punct,
                        result.url_num_digit,
                        result.url_num_mathces,
                        result.url_is_query]
            ret += "\t".join(map(str,features))
            ret += "\n"    
    return ret

def is_url_serp(url):
    if 'google.com/search' in url or 'http://ir-ub.mathcs.emory.edu/intent/user-study/tasks/' in url:
        return True
    else: return False

def get_result_rank(search_results, url):
    rank = -1
    for i in range(0, len(search_results) - 1):
        #print search_results
        if search_results[i][0] == url:
            rank = search_results[i][1]
            break
    return rank

def find_result(serps, search_results, serp_url, url):    
    query = ""
    serp_page_id = ""    
    rank = - 1
    distance = 0
    for i in range(len(serps) - 1, -1, -1):        
        distance += 1
        if serp_url == serps[i]['url']:
            serp_page_id = serps[i]['page_id']
            rank = get_result_rank(search_results[serp_page_id], url)
            break            
    return (serp_page_id, query, rank)
    
def add_count(x, k):
    if x.has_key(k):
        x[k] += 1
    else: x[k] = 1
    
def compute_ctrs():    
    views = {}
    views_before_last_click = {}
    views_exact = {}
    clicks = {}
    relevance_pool = {}
    serps = []
    search_results = {}    
    
    conn = psycopg2.connect(db_connect)    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT distinct user_id from emu_events")
    users = []
    for u in cur.fetchall():
        users.append(u[0])
    print users
            
    for uid in users:    
        cur.execute("SELECT * FROM search_results WHERE user_id = %s " % uid)
        for result in cur.fetchall():        
            if search_results.has_key(result['page_id']):                                                       
                search_results[result['page_id']].append([result['url'], result['rank']]) 
            else:                        
                search_results[result['page_id']] = [[result['url'], result['rank']]]                                              
        cur.execute("SELECT * FROM emu_events WHERE user_id = %s AND event_name = 'LocationChange0' ORDER BY ts " % uid)            
        for p in cur.fetchall():
            if is_url_serp(p['url']) == True: # SERP  
                serps.append(p)
                # add page view count
                if search_results.has_key(p['page_id']):                         
                    for result in search_results[p['page_id']]:
                        add_count(views, result[0])                                        
                                                
            elif is_url_serp(p['ref']): # click from SERP
                [serp_page_id, query, rank] = find_result(serps, search_results, p['ref'], p['url'])            
                # add page adjusted view count            
                for i in range(0, rank):
                    result = search_results[serp_page_id][i]
                    add_count(views_before_last_click, result[0])                                    
                add_count(clicks, p['url'])                        
         
        # compute exact views from gaze 
        
    # pool relevance 
    cur.execute("SELECT * FROM emu_events WHERE event_name = 'RelevanceLabel' order by ts ")
    for rel in cur.fetchall():
        if rel['relevance'] > 0:            
            if relevance_pool.has_key(rel['url']):                                
                tmp = relevance_pool[rel['url']]                
                tmp.append(rel['relevance'])
                relevance_pool[rel['url']] = tmp
            else:
                relevance_pool[rel['url']] = [rel['relevance']]
    # debug 
    
    #for u in relevance_pool:
    #    print u, ":\t", relevance_pool[u]
                
    
    ########################## AGGREGATE ########################
    relevance = {}
    for u in relevance_pool:
        relevance[u] = numpy.mean(relevance_pool[u])
    print "relevance_pool:\t", len(relevance)            
    print "views:\t", len(views)
    print "views_before_last_click:\t", len(views_before_last_click)
    print "clicks:\t", len(clicks)
    
    ctr = {}
    ctr_adjusted_views = {}
    ctr_gaze = {} # COV ratio     
    rel_vec = []
    ctr_vec = []
    ctr_adjusted_vec = []
    for u in relevance:
        if views.has_key(u):                                       
            ctr[u] =  float(clicks.get(u,0)) / (views[u])
            ctr_adjusted_views[u] = float(clicks.get(u,0)) / (views_before_last_click.get(u,1))
            rel_vec.append(relevance[u])
            ctr_vec.append(ctr[u])
            ctr_adjusted_vec.append(ctr_adjusted_views[u])
            print "%s,%s,%s;" % (ctr[u], ctr_adjusted_views[u], relevance[u])
    
             
    #for u in ctr:
    #    print "%s\t%s\t%s" % (ctr[u], ctr_adjusted_views[u], relevance[u] )            
    c_ctr =  pearsonr(numpy.vstack(ctr_vec), numpy.vstack(rel_vec))
    c_ctr_adjusted =  pearsonr(ctr_adjusted_vec, rel_vec)
    print c_ctr, c_ctr_adjusted 
    
    #print pearsonr(, y) 
    # calculate pearson correlation 
          
def main():
    # parse emu, gaze and merge
    process_log_data()    
    
    # dump relevance 
    #dump_relevance_data(page_relevance_out)

    # dump task success 
    #dump_feedback_data(task_feedback_out)
    
    # compute CTR's
    compute_ctrs()
    print "done"
    
if __name__ == "__main__":
    main()    
    