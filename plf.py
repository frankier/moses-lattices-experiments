'''Need to have hfst-lookup installed and Swedish transducer in directory'''
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
Returns word lattice in plf format
NB: HFST labels the compounds in terms of prefixes and main nouns (substantivs), so this labelling is continued here
'''

def make_plf(dic):
	analyzer = pexpect.spawnu('hfst-lookup swedish.hfst')
	analyzer.expect('> ')
	#print(str(len(dic)) + ' tokens in test')
	all_sets=[]
	for token in dic:
		#print('Analyzing', token, '...')
		analyzer.sendline( token )
		analyzer.expect('> ')
		hfst_result= analyzer.before
		hfst_result= hfst_result.split('0.000000')
		for subword in hfst_result:
			prefixes=[]
			substantivs=[]
			segment= re.search(r'(?:\w*[<>]+\w*)+', subword)
			if segment:
				segment= segment.group(0)
				prefix= re.search(r'\w+(?=\<prefix\>)', segment)
				if prefix:
					prefix= prefix.group(0)
					prefixes.append(prefix)
					substantiv= re.search(r'\w+(?=\<substantiv\>)', subword)
					if substantiv:
						substantiv= substantiv.group(0)
						substantivs.append(substantiv)

					'''Initializing all the distances involved'''
					if prefixes!=[]:
						prefix_prob=.5/len(prefixes)
						prefix_distance=1

					if substantivs!=[]:
						sub_prob=1/len(substantivs)
						sub_distance=1

					'''The total distance for the unsegmented noun'''
					if len(prefixes)>=len(substantivs):
						total_distance= len(prefixes)
					else:
						total_distance= len(substantivs)

					'''The unsegmented noun'''
					unsegmented=(token, .5, 2)

					'''The prefixes'''
					p_preset=[]
					for prefix in prefixes:
						if prefix!=token:
							p=(prefix, prefix_prob, prefix_distance)
							p_preset.append(p)
					p_set=tuple(p_preset)

					'''The substantivs'''
					s_preset=[]
					for sub in substantivs:
						if sub!=token:
							s= (sub, sub_prob, sub_distance)
							s_preset.append(s)
					s_set=tuple(s_preset)
					
					if p_set!=() and s_set!=():
						final_set=(unsegmented, p_set, s_set)
						all_sets.append(final_set)
				else:
					other= re.search(r'\w+(?=\<)', segment)
					other=other.group(0)
					final_set= (other, 1, 1)
					all_sets.append(final_set)

	all_sets=set(all_sets)
	return all_sets
		




dic= make_dic('en-sv.test.half')
print(make_plf(dic))
#print(dic)