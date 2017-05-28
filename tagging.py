'''
Need to have stagger.jar compiled under stagger directory (use ant)
'''

import sys
import pexpect

#with open('sample.txt') as stagger_analysis:

def make_lattice(stagger_analysis):
        
    #Make a dictionary of all edges and their scores for one analysis
    analyses = {}
    stagger_analysis = stagger_analysis.decode("utf-8")
    stagger_analysis = stagger_analysis.splitlines()
    in_analysis = True
    keys = []
    to_sum = []
    #Add new word analyses to the dictionary
    for line in stagger_analysis:
        line = line.rstrip('\n')
        line = line.split('\t')
        if len(line) == 1:
            in_analysis = False
        if in_analysis:
            line[5] = line[5].replace("|", ".")
            key = ''.join([line[1], "|", line[2], "|", line[4], "|", line[5]])
            to_sum.append(key)
            if key not in keys:
                keys.append(key)
                try:
                    analyses[line[0]][key] = 0
                except:
                    analyses[line[0]] = {key : 0}
        #When reaching the result line, add it to corresponding words
        if len(line) == 1 and line != ['']:
            for word in to_sum:
                for i in range(1,len(analyses)+1):
                    i = str(i)
                    try:
                        analyses[i][word] += float(''.join(line))
                    except:
                        pass
            if len(to_sum) == len(analyses):
                to_sum = []
        in_analysis = True
    print(analyses)

    #Create a lattice from the existing dictionary
    lattice = "("
    for i in range(1, len(analyses)+1):
        i = str(i)
        lattice += "("
        for edge in analyses[i]:
            score = str(analyses[i][edge])
            lattice_edge = "(" + edge + "," + score + ",1)"
            lattice += lattice_edge + ","
        lattice = lattice[:len(lattice)-1] + "),"
    lattice = lattice[:len(lattice)-1] + ")"
    print(lattice)
    return lattice # TODO

child = pexpect.spawn(
    "java -Xmx4g -jar stagger/stagger.jar -modelfile swedish.bin "
    "-posBeamSize 200 -multiple 10 -tag -")
child.expect('Loaded')

print('(')

# Input is in horizontal tokenized format, but stagger takes verical
for line in sys.stdin:
    for word in line.split(' '):
        child.send(word + '\n')
    child.send('\n')
    child.expect('\r\n\r\n')
    child.expect('\r\n\r\n\r\n')
    print(make_lattice(child.before))

print(')')
