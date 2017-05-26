'''
Need to have stagger.jar compiled under stagger directory (use ant)
'''

import sys
import pexpect

def make_lattice(stagger_analysis):
    pass  # TODO

child = pexpect.spawn(
    "java -jar stagger/stagger.jar -modelfile swedish.bin "
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
