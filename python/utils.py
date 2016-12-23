'''
Created on Mar 20, 2012

@author: dlagun
'''

import re, sys, os, urllib, datetime

def parse_emu_params (str):
    ret = {}
    s = str.split("&")        
    ret = parse_url_params(str)
    ret.setdefault('')        
    return ret

def parse_result_layout_data(str):
    items = str.split("|")
    ret = {}        
    for i in items:
        if i is not "":
            params = parse_url_params(i)         
            ret[params['id']] = params     
    return ret  
        
def parse_url_params(str):
    ret = {}    
    if '?' in str:
        s = str[str.index('?') + 1: len(str) ].split("&")        
    else: 
        s = str.split("&")
        
    for p in s:        
        ii = p.rfind("=")        
        p_name = p[0 : ii]        
        ret[p_name] = urllib.unquote(p[ii + 1 : len(p)].decode('utf-8'))        
    return ret

def clean_query(str):
    str = re.sub('\"','',str)
    str = re.sub('[+]',' ',str)
    str = re.sub('[\s]+',' ',str)
    str = re.sub('\A([:?!\s]+)','',str)
    str = re.sub('([:?!\s]+)\Z','',str)
    str = str.lower()
    return str
    
def milli_to_timestamp(millisecond):
    client_ts = datetime.datetime.fromtimestamp(millisecond / 1000)
    micros = divmod(millisecond, 1000)
    ts = client_ts.strftime("%Y-%m-%d %H:%M:%S") + "." + str(micros[1])
    return (client_ts,ts)