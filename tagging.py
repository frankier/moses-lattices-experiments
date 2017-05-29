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


def strify(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    return "'" + s + "'"


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
    to_sum = []

    # Add new word analyses to the dictionary
    for line in stagger_analysis:
        if len(line) == 1:
            in_analysis = False
        if in_analysis:
            key = line_to_factors(line, include_minor=include_minor)
            to_sum.append(key)
            if line[0] not in analyses:
                analyses[line[0]] = {key: 0}
            if key not in analyses[line[0]]:
                analyses[line[0]][key] = 0

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
    lattice = "("
    for i in range(1, len(analyses)+1):
        i = str(i)
        lattice += "("
        total = sum(analyses[i].values())
        for edge in analyses[i]:
            score = str(analyses[i][edge] / total)
            lattice_edge = "(" + strify(edge) + "," + score + ",1)"
            lattice += lattice_edge + ","
        lattice = lattice[:len(lattice)-1] + "),"
    lattice += ")"
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
    child.expect('Loaded.\r\n')
    child.setecho(False)
    child.waitnoecho()


def handle_output(handler, include_minor, output_end_delim):
    # child.expect('\r\n\r\n')
    child.expect(output_end_delim)
    print(handler(child.before, include_minor=include_minor))
    sys.stdout.flush()


def stream_gen(handler, include_minor, output_end_delim):
    # Input is in horizontal tokenized format, but stagger takes verical
    for i, line in enumerate(sys.stdin):
        for j, word in enumerate(line.split(' ')):
            child.send(word + '\n')
            # So this is tricky - stagger only outputs the anlysis after the
            # first token of the *next* sentence
            if i != 0 and j == 0:
                handle_output(handler, include_minor, output_end_delim)
        child.send('\n')
    child.sendcontrol('d')
    handle_output(handler, include_minor, output_end_delim)


def stream_lattice(include_minor=True):
    start_stagger(multiple=10)
    # Input is in horizontal tokenized format, but stagger takes verical
    stream_gen(lattice_sent, include_minor, '\r\n\r\n\r\n')


def stream_training(include_minor=True):
    start_stagger()
    stream_gen(training_sent, include_minor, '\r\n\r\n')


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
