''' 
Program assumes paths to Moses installed in the UU lingfil network.
Noun compounds with more than four subwords will not be recognized.

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
    lines= line.split(' ')
    for word in lines:
    	'''Finding compound segmentation'''
        analyzer= pexpect.spawnu('/local/kurs/mt/mosesdecoder/scripts/generic/compound-splitter.perl -model /home/m16/paupaw/nobackup/mtp/compound/cm/compound.model.sv')
        analyzer.sendline( word )
        analyzer.expect('\r\n')
        analyzer.expect('\r\n')
        splitter= analyzer.before
        compound= splitter.split(' ')

        '''Creating PLF tuples for compounds according to subword amount'''
        if len(compound)==1:
            towrite= (word, 1, 1)
            sys.stdout.write(str("(" + str(towrite) + ",)" + ","))
        if len(compound)==2:
            towrite= (word, .5, 2)
            towrite1= (compound[0], .5, 1)
            towrite2=(compound[1], 1, 1)
            sys.stdout.write(str("(" + str(towrite) + "," + str(towrite1)+ "),(" + str(towrite2)+ ",),"))
        if len(compound)==3:
            towrite= (word, .5, 3)
            towrite1= (compound[0], .5, 1)
            towrite2=(compound[1], 1, 1)
            towrite3=(compound[2], 1, 1)
            sys.stdout.write(str("(" + str(towrite) + "," + str(towrite1)+ "),(" + str(towrite2)+ ",)," + "(" + str(towrite3)+ ",),"))
        if len(compound)==4:
            towrite= (word, .5, 4)
            towrite1= (compound[0], .5, 1)
            towrite2=(compound[1], 1, 1)
            towrite3=(compound[2], 1, 1)
            towrite4=(compound[3], 1, 1)
            sys.stdout.write(str("(" + str(towrite) + "," + str(towrite1)+ "),(" + str(towrite2)+ ",)," + "(" + str(towrite3)+ ",),("+ str(towrite4) + ",),"))
    print(")")


