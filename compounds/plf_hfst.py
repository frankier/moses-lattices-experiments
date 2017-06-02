'''
Program assumes hfst-lookup is installed and that the Swedish transducer is in the working directory.

Input: text file with Swedish sentences, separated by a new line
Output: Each line converted to PLF
'''

import os
import pexpect
import re
import sys

for line in sys.stdin:
	sys.stdout.write("(")
	line=line.strip()
	words= line.split(' ')
	for word in words:

		'''Accounting for words with quotes (special characters)'''
		if re.search(r'\"', word) != None:
			text = re.sub(r'(")', r'\"', word)
			word = text

		if re.search(r'\'', word) != None:
			text = re.sub(r'(\')', r'\1\\\'', word)
			word= text

		'''Finding compound segmentation'''
		analyzer = pexpect.spawnu('hfst-lookup swedish.hfst')
		analyzer.expect('> ')
		analyzer.sendline( word )
		analyzer.expect('> ')
		hfst_result= analyzer.before
		hfst_result= hfst_result.strip()
		hfst_result= hfst_result.split('0.000000')
		words=[]
		prefixes=[]
		substantivs=[]
		for subword in hfst_result:
			token_s= re.search(r'(?:\w*)', subword)
			if token_s:
				if token_s!= '': 
					token= token_s.group(0)
			else:
				pass


			'''For misc'''
			easy_list=['konjunktion', 'adjektiv', 'interjektion', 'adverb', 'pronomen', 'verb', 'substantiv']
			for label in easy_list:
				regex= re.compile(r'label')	
				no_compound= re.search(regex, subword)
				if no_compound:
					if word not in words:
						words.append(word)
						pass


			'''For nouns'''
			noun= re.search(r'substantiv', subword)
			if noun:
				'''For definite nouns'''
				end=re.search(r'(?:en)$|(?:et)$', word)
				if end:
					f= re.search(r'\w+\<prefix\>\w+\<prefix\>\w?e[nt]\<substantiv\>\<(utrum|neutrum)\>\<sg\>\<obest\>\<nom\>|\w+\<prefix\>\w+\<substantiv\>\<(utrum|neutrum)\>\<sg\>\<best\>\<nom\>', subword)
					if f:
						f= f.group(0)
						f2= re.findall(r'\w+(?=\<prefix\>)', f) #reverse order
						w= word.split(f2[0]) #the substantiv
						article_list=['en', 'et']
						if w[1] not in substantivs and w[1] not in article_list:
							substantivs.append(w[1])
						if substantivs!=[] and w[1] not in article_list and f2[0] not in prefixes:
							prefixes.append(f2[0])
						pass


				'''For plural nouns'''
				plural_x=['ar', 'or', 'er']
				for x in plural_x:
					regex= re.compile(r".*(?=ar\<" +x + ")")
					plural= re.search(regex, subword)
					if plural:
						plural= plural.group(0)
						end= re.findall(r'(?:\w+)(?=\<)', plural)
						if len(end)==2:
							if end[0] not in prefixes:
								prefixes.append(end[0])
							full=end[1] + 'ar'
							if full not in substantivs:
								substantivs.append(full)
						if len(end)==1:
							if word not in words:
								words.append(word)
						pass


				'''For plurals ending in -na'''
				if words == [] and prefixes == [] and substantivs == []:
					if word.endswith('na'):
						na= re.search(r'\w*(?=\<prefix\>\w+\<substantiv\>\<utrum\>\<pl\>\<best\>\<nom\>)', subword)
						if na:
							na= na.group(0)
							if na not in prefixes:
								prefixes.append(na)
							omg= word.split(na)
							if omg[1] not in substantivs:
								substantivs.append(omg[1])
					pass


				'''For genitive cases'''
				if words == [] and prefixes == [] and substantivs == []:
					if word.endswith('s'):
						f= re.search(r'\w+\<prefix\>\w{3,10}\<substantiv\>\<(utrum|neutrum)\>\<sg\>\<obest\>\<gen\>', subword)
						if f:
							f= f.group(0)
							f2= re.findall(r'\w+(?=\<prefix\>)', f)
							if f2[0] not in prefixes and f2[0] not in substantivs:
								prefixes.append(f2[0])
							w= word.split(f2[0])
							if w[1] not in substantivs and w[1] not in prefixes:
								substantivs.append(w[1])
						else:
							pass
					else:
						pass
							

				if not word.endswith('s'):
					final= re.search(r'\w+\<prefix\>\w+\<substantiv\>\<(utrum|neutrum)\>\<sg\>\<obest\>\<nom\>', subword)
					if final:
						finals=re.search(r'\w+(?=\<substantiv\>)', subword)
						if finals:
							finals=finals.group(0)
							article_list=['en', 'et', 'ar', 'or', 'er']
							if finals not in substantivs and finals not in article_list:
								substantivs.append(finals)
							if substantivs!=[]:
								finalp=re.search(r'\w+(?=\<prefix\>)', subword)
								if finalp:
									finalp=finalp.group(0)
									if finalp not in prefixes:
										prefixes.append(finalp)

		'''Creating the PLF tuples''' 
		if words == []:
			words.append(word)
			
		if prefixes!=[]:
			prefix_prob=.5/len(prefixes)
			prefix_d=1

		if substantivs!=[]:
			sub_prob=1/len(substantivs)
			sub_d=1

		convertlist=[]
		convert_plist=[]
		convert_slist=[]
		if prefixes==[] and substantivs==[]:
			x= (word, 1, 1)
			convert_plist.append(x)
		else:
			convert_plist.append((word, .5, 2))
			for x in prefixes:
				convert_plist.append((x, prefix_prob, prefix_d))
			for x in substantivs:
				convert_slist.append((x, sub_prob, sub_d))
		
		convertlist.append(convert_plist)
		if convert_slist!=[]:
			convertlist.append(convert_slist)

		convertlist= tuple(convertlist)
		for l in convertlist:
			sys.stdout.write(str(tuple(l)) + ",")

	print(")")



