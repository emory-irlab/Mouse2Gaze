# -- Writtenb by dsavenk

import psycopg2
from os import path
import re
import urllib2
#import emu_load_snippets
from BeautifulSoup import BeautifulSoup
#from html_resource_save import resource_extractor
import urllib
import httplib
import socket
#prefix = emu_load_snippets.prefix
prefix = 'dg21'
socket.setdefaulttimeout(5)

SE_GOOGLE = "google"
SE_BING = "bing"
SE_YAHOO = "yahoo"

class SearchResult(object):
    def __init__(self, url = "", title = "", snip_body = "", snip_html = "", res_pos = -1, res_id = "", title_html = ""):
        self.url = url
        self.title = title
        self.snip_body = snip_body
        self.snip_html = snip_html
        self.res_pos = res_pos
        self.res_id = res_id
        self.title_html = title_html

    def url(self, url):
        self.url = urllib.unquote(url)

        
def get_search_engine_name(url):
    if url.find("google.com/search") != -1:
        return SE_GOOGLE
    elif url.find("bing.com/search") != -1:
        return SE_BING
    elif url.find("yahoo.com/search") != -1:
        return SE_YAHOO
    return None

# disabled right now 
def util_load_serps(dbhost, dbport, dbname, table_name, documents_root, user, password):
    connection = psycopg2.connect(host = dbhost, port = dbport, user = user, password = password, database = dbname)
    cursor = connection.cursor()
    select_serps = """SELECT query, url, content_id, content_path FROM %s
                      WHERE event_name = 'contentCache'
                   """ % table_name
    cursor.execute(select_serps)
    rec = cursor.fetchone()
    not_found = []
    count = 0
    added = set([])
    while rec:
        search_engine = get_search_engine_name(rec[1])
        if search_engine:
            file_path = documents_root + "/".join([rec[3].strip(),rec[2].strip()]) + ".html"
            if path.exists(file_path):
                inp = open(file_path, "r")
                page_html = inp.read()
                inp.close()
                (results, results_cnt) = parse_serp(search_engine, page_html)
                for result in results:
                    if result.url not in added:
                        url = result.url
                        if url.startwith("/http/"):
                            url = "http://" + url.strip("/http/")
                        #jsnipobj = JudgementObject(url = url, title = result.title, snippet_body = result.snip_body, snippet_html = result.snip_html)
                        #jdocobj = JudgementObject(url = url, title = None, snippet_body = None, snippet_html = None)
                        #jsnipobj.save()
                        #jdocobj.save()
                        added.add(result.url)
                        count += 1
            else:
                not_found.append(file_path)
            
        rec = cursor.fetchone()
    connection.close()
    return (count, not_found)

def parse_serp(search_engine, html):
    html_soup = BeautifulSoup(html)
    serp = None
    if search_engine == SE_GOOGLE:
        serp = parse_google_serp(html_soup)
    elif search_engine == SE_YAHOO:
        serp = parse_yahoo_serp(html_soup)
    elif search_engine == SE_BING:
        serp = parse_bing_serp(html_soup)
    return serp

def parse_google_serp(html_soup):
    div_result_cnt = html_soup.find('div', id='resultStats')
    result_cnt = None
    if div_result_cnt:
        m = re.search(r'(\d+) result', div_result_cnt.text.replace(',', ''))
        if m: result_cnt = int(m.group(1))

    resdiv = html_soup.find('div', id='ires')
    if resdiv is None:
        return ([], 0)
    reslist = resdiv.findAll('li', { 'class': re.compile(r'\bg\b') })
    snippet_num = 0
    search_results = []
    for res in reslist:       
            snippet_num += 1
            snippet_html = str(res)
            snippet_text = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', snippet_html)).strip()
            res_h3 = res.find('h3')        
            if res_h3 is None:
                snippet_href = ''
                snippet_title = ''
                search_results.append(SearchResult(snippet_href, snippet_title, snippet_text, snippet_html, snippet_num, res['id']))
                continue
            res_l = res_h3.find('a')
            if res_l is not None:                
                snippet_href = res_l.get('href')
                snippet_title = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', str(res_l))).strip()        
            else:
                snippet_href = ''
                snippet_title = ''
            search_results.append(SearchResult(snippet_href, snippet_title, snippet_text, snippet_html, snippet_num, res['id'], res_h3))
            
            #try: snippet_cached_href = [a.get('href') for a in res.findAll('a') if a.text == 'Cached'][0]
            #except: snippet_cached_href = None

    return (search_results, result_cnt)

def parse_yahoo_serp(html_soup):
    div_result_cnt = html_soup.find('strong', id='resultCount')
    result_cnt = None
    if div_result_cnt:
        result_cnt = int(div_result_cnt.text.replace(',', ''))

    resdiv = html_soup.find('div', id='web')
    reslist = resdiv.findAll('div', {'class': re.compile(r'\bres\b')} )
    snippet_num = 0
    search_results = []
    for res in reslist:
        snippet_num += 1
        snippet_html = str(res)
        snippet_text = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', snippet_html)).strip()
        res_l = res.find('a', { 'class': 'yschttl spt' } )
        snippet_href = res_l.get('href')
        if "**http" in snippet_href:
            snippet_href = re.sub(r'.*\*\*', '', snippet_href)
            snippet_href = urllib.unquote(snippet_href)
        snippet_title = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', str(res_l))).strip()
        search_results.append(SearchResult(snippet_href, snippet_title, snippet_text, snippet_html, snippet_num, res['id']))
    
    return (search_results, result_cnt)
"""        
def fetch_url(page_url, base_dir, filename):            
    success = False
    try :
        # set game cookie to pass the authentication
        opener = urllib2.build_opener()        
        opener.addheaders =[('User-agent', 'Mozilla/5.0')]
        opener.addheaders.append(('Cookie', 'hitid=' + emu_load_snippets.secret_cookie))        
        if page_url[0] != '/':
            page_url = '/' + page_url        
        #f = opener.open('http://ir-ub.mathcs.emory.edu:8100'+page_url)
        f = opener.open(page_url.replace('/http/','http://'))
        html = f.read()        
        o = open(base_dir + "/" + filename, 'w+')
        o.write(html)
        o.close()
        f.close();
        success = True
    except Exception, err:        
        print 'page downloader ERROR: %s \t %s \t %s \n' % (page_url.replace('/http/','http://'), filename, str(err))
    try:    
        # fetch resources if any
        extractor = resource_extractor(base_dir + "/")
        extractor.extract_html_resources(page_url.replace('/http/','http://'), base_dir + "/" + filename)
    except Exception, err:        
        print 'extractor : ERROR: %s\n' % str(err) 
    return success
                 
def fetch_snippet_resources(base_dir, snip_id, snip_html):
    soup = BeautifulSoup(snip_html)
    res_cnt = 0
    success = False                            
    for tag in soup.find('h3'):                              
        res_filename =  '%s_%s.html' % (snip_id, res_cnt)        
        #if 'webcache.googleusercontent.com' in tag['href'] or len(tag['href']) < 2 or 'http://ir-ub.mathcs.emory.edu/' in tag['href']:
        #    continue                
        print tag['href']       
        s = fetch_url(tag['href'], base_dir, res_filename)
        s = True
        if res_cnt == 0:
            success = s
        tag['href'] = 'http://ir-ub.mathcs.emory.edu/snippets/%s/landing_pages/'% prefix + res_filename
        res_cnt +=1    
    return (soup.prettify(), success)
"""    
    
def parse_bing_serp(html_soup):
    div_result_cnt = html_soup.find('span', id='count')
    result_cnt = None
    if div_result_cnt:
        m = re.search(r'(\d+) result', div_result_cnt.text.replace(',', ''))
        if m: result_cnt = int(m.group(1))

    resdiv = html_soup.find('div', id='results')
    reslist = resdiv.findAll('li', { 'class': 'sa_wr'} )
    snippet_num = 0
    search_results = []
    for res in reslist:
        snippet_num += 1
        snippet_html = str(res)
        snippet_text = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', snippet_html)).strip()
        res_h3 = res.find('h3')
        res_l = res_h3.find('a')
        snippet_href = res_l.get('href')
        snippet_title = re.sub(r'\s+', ' ', re.sub(r'<.*?>', ' ', str(res_l))).strip()

        search_results.append(SearchResult(snippet_href, snippet_title, snippet_text, snippet_html, snippet_num))
        
    return (search_results, result_cnt)

#to avoid incomplete reads
def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial

    return inner
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)