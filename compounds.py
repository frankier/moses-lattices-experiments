'''
Need to have hfst-lookup installed and Swedish transducer in directory
'''

import os
import pexpect
import re



'''
Input: tokenized (Swedish) text file
Returns a dictionary with token as a key and empty dictionary as a value
'''
def make_dic(svfile):
	dic={}
	with open(svfile, 'r') as f:
		x=f.readlines()
		for item in x:
			item=item.lower()
			item=item.strip()
			tokens= re.findall(r'[a-zäåö]+', item)
			for token in tokens:
				if token not in dic:
					dic[token]={}
	return dic



'''
Input: Dictionary from make_dic
Returns a dictionary of token with an embedded dictionary with the token's subwods, length in sub words, and score
'''
def run_analyzer(dic):
	analyzer = pexpect.spawnu('hfst-lookup swedish.hfst')
	analyzer.expect('> ')
	print(str(len(dic)) + ' tokens in test')
	for token in dic:
	    print('Analyzing', token, '...')
	    analyzer.sendline( token )
	    analyzer.expect('> ')
	    hfst_result= analyzer.before
	    hfst_result= hfst_result.split('0.000000') #split each result 
	    subword_lst=[]
	    for subword in hfst_result:
	    	extract= re.findall(r'\w+(?=\<\w*\>)', subword) #extract the subwords from each hfst analysis
	    	if extract:
	    		subword_lst.append(set(extract))
	    maxl= 1
	    for subwords in subword_lst:
	    	if len(subwords)> maxl:
	    		maxl= len(subwords) 
	    dic[token]['subwords']= subword_lst
	    dic[token]['length_in_subwords']= maxl
	    dic[token]['score']= 1/maxl
	return dic





dic= make_dic('en-sv.test.sv')
run_analyzer(dic)
#moses-udpipe-lattices
