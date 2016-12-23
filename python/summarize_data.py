'''
Created on May 1, 2012

@author: dlagun
'''

import sys, psycopg2,psycopg2.extras
import numpy

db_connect = "dbname='m2g' user='dlagun' password='lagoon12345' host='localhost'"
conn = psycopg2.connect(db_connect)    
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

data = []
mx = -1
tasks = []
for task_idx in range(0, 12):
    diff = []
    succ = []    
    cur.execute("SELECT * FROM emu_events WHERE event_name = 'TaskFeedback' and task_idx = %s " % task_idx)
    for row in cur.fetchall():
        if row['success'] > 0:
            succ.append(row['success'])
        if row['difficulty'] > 0:
            diff.append(row['difficulty'])    
    #print "task %s:\t s = %s\t d = %s\t len = %s " % (task_idx, numpy.mean(succ), numpy.mean(diff), len(diff))    
    #print diff
    data.append(diff)
    tasks.append([task_idx, numpy.mean(diff)])
    if mx < len(diff):
        mx = len(diff)
        
tasks_sorted = sorted(tasks, key=lambda x: x[1], reverse=True)
task_idx = 0
for task in data:
    task_idx += 1
    for v in task:
        print  v, "\t\"", task_idx,"\""
             
# print task 

# export data to R 
for i in range (0, mx):    
    for j in range(0,12):
        if len(data[j]) > i:
            print data[j][i], ",",
        else: print ",",
    print ""
    
    




     
        
        
    