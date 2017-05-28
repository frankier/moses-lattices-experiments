'''
Need to have stagger.jar compiled under stagger directory (use ant)
'''

import sys
import pexpect


def line_to_factors(line_bits, include_minor=True):
    minor_pos = line_bits[4] + "." + line_bits[5].replace("|", ".")
    factors = [line_bits[1], line_bits[2], line_bits[4]]
    if include_minor:
        factors.append(minor_pos)
    return '|'.join(factors)


def proc_stagger_out(stagger_out):
    stagger_out = stagger_out.decode("utf-8")
    stagger_out = stagger_out.splitlines()
    return (
        line.rstrip('\n').split('\t')
        for line in stagger_out)


def lattice_sent(stagger_analysis, include_minor=True):
    # Make a dictionary of all edges and their scores for one analysis
    analyses = {}
    stagger_analysis = proc_stagger_out(stagger_analysis)
    in_analysis = True
    keys = []
    to_sum = []

    # Add new word analyses to the dictionary
    for line in stagger_analysis:
        if len(line) == 1:
            in_analysis = False
        if in_analysis:
            key = line_to_factors(line, include_minor=include_minor)
            to_sum.append(key)
            if key not in keys:
                keys.append(key)
                try:
                    analyses[line[0]][key] = 0
                except:
                    analyses[line[0]] = {key: 0}

        # When reaching the result line, add it to corresponding words
        if len(line) == 1 and line != ['']:
            for word in to_sum:
                for i in range(1, len(analyses)+1):
                    i = str(i)
                    try:
                        analyses[i][word] += float(''.join(line))
                    except:
                        pass
            if len(to_sum) == len(analyses):
                to_sum = []
        in_analysis = True

    # Create a lattice from the existing dictionary
    lattice = ""
    for i in range(1, len(analyses)+1):
        i = str(i)
        lattice += "("
        total = sum(analyses[i].values())
        for edge in analyses[i]:
            score = str(analyses[i][edge] / total)
            lattice_edge = "(" + repr(edge) + "," + score + ",1)"
            lattice += lattice_edge + ","
        lattice = lattice[:len(lattice)-1] + "),"
    return lattice


def training_sent(stagger_analysis, include_minor=True):
    stagger_analysis = proc_stagger_out(stagger_analysis)
    sent_out = []
    for line in stagger_analysis:
        sent_out.append(line_to_factors(line, include_minor=include_minor))
    return ' '.join(sent_out)


def start_stagger(multiple=None, beam_size=200):
    global child
    if multiple is not None:
        mult_opt = "-multiple {} ".format(multiple)
    else:
        mult_opt = ""
    child = pexpect.spawn(
        ("java -Xmx4g -jar stagger/stagger.jar -modelfile swedish.bin "
         "-posBeamSize {} {}-tag -").format(beam_size, mult_opt))
    child.expect('Loaded')


def stream_lattice(include_minor=True):
    start_stagger(multiple=10)
    sys.stdout.write('(')
    sys.stdout.flush()

    # Input is in horizontal tokenized format, but stagger takes verical
    for line in sys.stdin:
        for word in line.split(' '):
            child.send(word + '\n')
        child.send('\n')
        child.expect('\r\n\r\n')
        child.expect('\r\n\r\n\r\n')
        sys.stdout.write(lattice_sent(
            child.before, include_minor=include_minor))
        sys.stdout.flush()

    sys.stdout.write(')\n')
    sys.stdout.flush()


def stream_training(include_minor=True):
    start_stagger()

    # Input is in horizontal tokenized format, but stagger takes verical
    for line in sys.stdin:
        for word in line.split(' '):
            child.send(word + '\n')
        child.send('\n')
        child.expect('\r\n\r\n')
        child.expect('\r\n\r\n')
        print(training_sent(
            child.before, include_minor=include_minor))
        sys.stdout.flush()


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'lattice':
        stream_lattice()
    elif arg == 'latticemaj':
        stream_lattice(False)
    elif arg == 'train':
        stream_training()
    elif arg == 'trainmaj':
        stream_training(False)
    else:
        print("Usage {} lattice|latticemaj|train|trainmaj".format(sys.argv[0]))
