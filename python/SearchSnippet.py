'''
Created on May 9, 2012

@author: dlagun
'''

import re
import nltk
import numpy
from math import sqrt
from textUtils.match import *
from textUtils.similarity import *
from textUtils.utils import *
from BeautifulSoup import BeautifulSoup
 
class SearchSnippet():
    
    def __init__(self, url, title, snip_body, snip_html, title_html,
                                 res_pos, res_id, coordinates, content_id,  
                                 query_string = "", serp_url = ""):
        self.url = url
        self.title = title
        self.title_html = title_html
        self.snip_body = snip_body
        self.snip_html = snip_html
        self.res_pos = res_pos # rank
        self.res_id = res_id 
        self.serp_url = serp_url
        self.query_string = query_string
               
        
        # layout information 
        self.x0 = coordinates['x0']
        self.y0 = coordinates['y0']
        self.cw = coordinates['cw']
        self.ch = coordinates['ch']
        
        # content cache id
        self.content_id = content_id
        
        # basic tokenization
        stop_word_list = nltk.corpus.stopwords.words('english')
        
        title_word_list = nltk.word_tokenize(title)
        title_word_list_wsw = [w for w in title_word_list if not w in stop_word_list] 
        title_fragments = title.split('...')
        title_bolded_word_list = get_bolded_terms(title_html)
        
        snip_body_word_list = nltk.word_tokenize(snip_body)
        snip_body_word_list_wsw = [w for w in snip_body_word_list if not w in stop_word_list]
        snip_body_fragments = snip_body.split('...')
        snip_body_bolded_word_list = get_bolded_terms(BeautifulSoup(snip_html))
        
        url_word_list = nltk.word_tokenize(url)
        
        query_word_list = nltk.word_tokenize(title)                        
                                       
                
        #################### TITLE FEATURES ####################################
        
        self.title_length_words = len(title_word_list)
        self.title_length_char =  len(title)               
        self.title_frac_sw =  len(title_word_list_wsw) * 1.0 /  (len(title_word_list) +  1.0)
        self.title_num_fragments = len(title_fragments)
        [self.title_num_cap, self.title_num_punct, self.title_num_digit] = num_chars(title)
        self.title_num_cap_per_word = self.title_num_cap / (1.0 + self.title_length_words)
        self.title_num_cap_per_fragment = self.title_num_cap / (1.0 + self.title_num_fragments)
        self.title_avg_fragment_length = numpy.mean(map(len, title_fragments))
        
        title_matches = num_of_matches(query_word_list, title_word_list)
        self.title_num_mathces = numpy.sum(title_matches)        
        
        # bold 
        self.title_lenght_bolded_words = len(title_bolded_word_list)
        self.title_lenght_bolded_chars = numpy.sum(map(len, title_bolded_word_list))
        self.title_frac_bolded = self.title_lenght_bolded_words / (1.0 + self.title_length_words)
                
        #################### BODY FEATURES ####################################
        self.snip_body_length_words = len(snip_body_word_list)
        self.snip_body_length_char =  len(snip_body)
        self.snip_body_frac_sw = len(snip_body_word_list_wsw) * 1.0 /  (1.0 + len(snip_body_word_list))
        self.snip_body_num_fragments = len(snip_body_fragments)
        [self.snip_body_num_cap, self.snip_body_num_punct, self.snip_body_num_digit] = num_chars(snip_body)
        self.snip_body_num_cap_per_word = self.snip_body_num_cap / (1.0 + self.snip_body_length_words)
        
        self.snip_body_num_cap_per_fragment = self.snip_body_num_cap / (1.0 + self.snip_body_num_fragments)
        self.snip_body_avg_fragment_length = numpy.mean(map(len, snip_body_fragments))                           
        
        body_matches = num_of_matches(query_word_list, snip_body_word_list)
        self.snip_body_num_mathces = numpy.sum(body_matches)
        
        # bold 
        self.snip_body_lenght_bolded_words = len(snip_body_bolded_word_list)
        self.snip_body_lenght_bolded_chars = numpy.sum(map(len, snip_body_bolded_word_list))
        self.snip_body_frac_bolded = self.snip_body_lenght_bolded_words / (1.0 + self.snip_body_length_words)
        
        #################### URL FEATURES ####################################
        self.url_length_char = len(url)
        [self.url_num_cap, self.url_num_punct, self.url_num_digit] = num_chars(url)
       
        url_matches = num_of_matches(query_word_list, url_word_list)
        self.url_num_mathces = numpy.sum(url_matches)
        self.url_is_query = 1 if query_string in url else 0        