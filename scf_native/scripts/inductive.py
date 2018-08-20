#!/usr/bin/env python

from __future__ import division

from operator import itemgetter, attrgetter

import sys
import re

target_verb = eval(sys.argv[1])
thresh = sys.argv[2]
parser_format = sys.argv[3]
parser_output = sys.argv[4]
target_gr_types = eval(sys.argv[5])
ignore_instance_gr_types = eval(sys.argv[6])
pos_groups = eval(sys.argv[7])
gr_types_to_deppos = eval(sys.argv[8])
gr_types_to_child = eval(sys.argv[9])
gr_types_to_lex = eval(sys.argv[10])

# parameters: fixed
grouppreps = False

# constants for indexing into GR.arg
HED = 0
DEP = 1

# count how many verb instances. just use a global for quick and easy solution
numvi = 0

# parameters: user-configurable

# NEED TO PARAMETERIZE THIS for WHICH RELATION IT IS.
# RELATIVE TO GR_TYPES_TO_LEX
# dirpreps = ["about", "behind", "beyond", "in", "on", "outside", "throughout", "up", "across", "below", "by", "inside", "onto", "over", "to", "along", "beneath", "down", "into", "out", "past", "toward", "via", "around", "between", "from", "off", "through", "toward"]
dirpreps = []


# auto-create a simpler data structure for reducing pos tags
pos_reduction_lookup = {}
for key, patterns in pos_groups.iteritems():
    for pattern in patterns:
        pos_reduction_lookup[re.compile(pattern)] = key 


def reduce_pos(string, label):   # if label is empty, use full pos reduction list
    "not sure which class this properly belongs to"
    for regexp in pos_reduction_lookup:
        if regexp.search(string):
            posgroup = pos_reduction_lookup[regexp]
            if label == "" or (label in gr_types_to_deppos and posgroup in gr_types_to_deppos[label]):
                return posgroup
    return "OTH"

# def reduce_label(string):
#     "puts in our abbreviations for gr labels, rasp-specific"
#     "and not sure which class it belongs to"
#     if string == 'ncsubj':
#         return 'su'
#     elif string == 'dobj':
#         return 'do'
#     elif string == 'iobj':
#         return 'io'
#     elif string == 'ncmodprt':
#         return 'ncp'
#     elif string == 'obj2':
#         return 'ob'
#     elif string == 'pcomp':
#         return 'pc'
#     elif string == 'ccomp_':
#         return 'cc'
#     elif string == 'ccompthat':
#         return 'cct'
#     elif string == 'xcomp_':
#         return 'xc'
#     elif string == 'xcompto':
#         return 'xct'
#     elif string == 'csubj_':
#         return 'cs'
#     elif string == 'csubjthat':
#         return 'cst'
#     elif string == 'xsubj_':
#         return 'xs_'
#     else:
#         return 'unk'

def reduce_label(string):
    return string

class LexiconEntry:
    "stores lemma, frame, and value"
    "the value may be freq or relfreq depending on which lexicon it's in"
    def __init__(self, lemma, frame, value):
        self.lemma = lemma
        self.frame = frame
        self.value = value

    def output(self):
        if float(self.value) > float(thresh):
            print "%s     %s     %.4f" % (self.lemma, self.frame, self.value)

class SubLexicon:
    "one part of a lexicon, e.g. frequencies or relative frequencies"
    def __init__(self):
        self.entries = []

    def has_entry(self, lemma, frame):
        for e in self.entries:
            if e.lemma == lemma and e.frame == frame:
                return True
        return False

    def increment(self, lemma, frame):
        for e in self.entries:
            if e.lemma == lemma and e.frame == frame:
                e.value = e.value + 1
                return
        self.add_entry(lemma, frame, 1)

    def add_entry(self, lemma, frame, value):
        self.entries.append(LexiconEntry(lemma, frame, value))

class Lexicon:
    "stores verbs, frames, frequencies, and relative frequencies"
    "relfreq dictionary calculated from freq"
    def __init__(self):
        self.freq = SubLexicon()
        self.relfreq = SubLexicon()
        self.totals = {}

    def increment(self, info):  # needs typecheck
        "increments frequency count for this lemma and frame"
        lemma, frame = info
        self.freq.increment(lemma, frame)
        if self.totals.has_key(lemma):
            self.totals[lemma] = self.totals[lemma] + 1
        else:
            self.totals[lemma] = 1

    def calc_rel_freqs(self):
        "calculates relative frequencies from frequencies"
        for e in self.freq.entries:
            self.relfreq.add_entry(e.lemma, e.frame, e.value / self.totals[e.lemma])

    def output(self, thresh):
        "prints out lexicon"
        s = sorted(self.relfreq.entries, key=attrgetter('value'), reverse=True)
        for e in sorted(s, key=attrgetter('lemma')):
            e.output()

    def instances(self,lemma):
        "returns number of instances in lexicon for a given lemma"
        if self.totals.has_key(lemma):
            return self.totals[lemma]
        else:
            return 0

class GR:
    "one grammatical relation: label, 2 args (we are assuming binary grs) (head, dependent)"
    "Allowed to have a child GR. Cheap workaround for a graph."
    def __init__(self, arg_array):
        if len(arg_array) == 3:
            self.label = arg_array[0]
            self.arg = arg_array[1:]
            self.childGR = 0
        # give error if length not 3

    def output(self):
        sys.stdout.write(self.label + " ")
        self.arg[HED].output()
        sys.stdout.write(" ")
        self.arg[DEP].output()
        sys.stdout.write("\n")

    def add_child(self, gr):
        self.childGR = gr

    def scf_component(self):
        "returns information about this GR relevant to an scf"
        "e.g. label, or label+complement pos, or label + lexicalized dependent"
        newlabel = reduce_label(self.label)
        info = newlabel
        # add POS tag of dependent if desired
        if self.label in gr_types_to_deppos:
            info = info + "_" + reduce_pos(self.arg[DEP].pos, self.label)
        # add lexicalization if desired
        if self.label in gr_types_to_lex and reduce_pos(self.arg[DEP].pos, self.label) in gr_types_to_lex[self.label]:
            lexinfo = self.arg[DEP].lemma.lower()
            if grouppreps:
                if self.label == "iobj":  # need this to not be hard coded
                    if lexinfo in dirpreps:
                        lexinfo = "DIR"
                    else:
                        lexinfo = "PREP"
            info = info + "-" + lexinfo
        # add information about child; assume if there is a child the info is desired
        if self.childGR:
            childlabel = reduce_label(self.childGR.label)
            info = info + "=>" + childlabel + "_" + reduce_pos(self.childGR.arg[DEP].pos, self.childGR.label)
        return info

    def match_gr(self, gr):
        if gr.arg[HED].index == self.arg[HED].index and gr.arg[DEP].index == self.arg[DEP].index and gr.label == self.label:
            return True
        return False

class Word:
    "one word with lexical item and pos tag, used as args in GRs"
    def __init__(self, lemma, index, pos):  # type check needed
        self.lemma = lemma
        self.index = index
        self.pos = pos

    def output(self):
        sys.stdout.write(self.lemma + "_" + self.index + "_" + self.pos)

class Sentence:
    "one sentence, arbitrary number of verb instances"
    def __init__(self):
        self.verb_instances = []

    def add_verbinstance(self, vi):
        "returns reference to verb instance, which is either the original"
        "if new, or an existing verb instance for this sentence if I already know about it"
        for existing_vi in self.verb_instances:
            if existing_vi.match_vi(vi):
                return existing_vi
        self.verb_instances.append(vi)
        return vi

    def build_scfs(self):
        self.scfs = []
        for vi in self.verb_instances:
            scf = vi.build_scf()
            if scf:
                self.scfs.append([vi.lemma, scf])
        return self.scfs

class SCF:
    "one SCF"
    def __init__(self):
        self.components = []

    def output(self):
        string = ""
        for c in sorted(self.components):
            string += c.output + ""
        return string

class SCFComponent:
    "a component of an SCF, e.g. a GR label, could have lexicalization"
    def __init__(self, label, deppos, headlex):
        self.label = label
        self.headlex = headlex
        self.deppos = deppos
    
    def output(self):
        string = label + "|" + deppos + "|" + headlex

class VerbInstance:
    "one verb instance in a sentence"
    def __init__(self, lemma, index):   # check string, numeric
        self.lemma = lemma
        self.index = index
        self.grs = []
        self.ignore = False
    
    def add_gr(self, gr):
        for existing_gr in self.grs:
            if existing_gr.match_gr(gr):
                return
        self.grs.append(gr)

    def match_gr(self, gr):
        if gr.arg[HED].index == self.index:
            return True
        return False

    def match_vi(self, vi):
        if vi.index == self.index:
            return True
        return False

    def build_scf(self):
        if self.ignore == True:
            return ""
        components = []
        for gr in self.grs:
            components.append(gr.scf_component())
        if parser_format == 'rasp' and "xs_" not in components and "cs_" not in components and "cst" not in components: # check for clausal subj:
            components.append("su")
        scf = ":".join(sorted(components))
        return scf

    def set_ignore(self):
        self.ignore = True
            
class InputManager:
    "high-level class for managing the file input, abstracted away from parser format"
    def __init__(self, filename, lexicon):
        if parser_format == 'rasp':
            self.rasp = RASP(filename)
        elif parser_format == 'conll':
            self.conll = CONLL(filename)
        self.lex = lexicon

    def read_input(self):
        "processes all sentences from input file"
        numvi = 0
        if parser_format == 'rasp':
            re_vpos = re.compile('^V')
        elif parser_format == 'conll':
            re_vpos = re.compile('^V')
        while True:
            sent_grs = self.get_sentence()
            if type(sent_grs) is str and sent_grs == "EOF":
                break
            if not sent_grs:
                continue               # empty grs indicates a parse failure
            s = Sentence()
            for g in sent_grs:
                if re_vpos.match(g.arg[HED].pos) and g.arg[HED].lemma in target_verb:
                    vi = s.add_verbinstance(VerbInstance(g.arg[HED].lemma, g.arg[HED].index))   # inefficient: should be able to go once through the GRs
                    for g2 in sent_grs:
                        if vi.match_gr(g2) and g2.label in ignore_instance_gr_types:
                            vi.set_ignore()
                        elif vi.match_gr(g2) and g2.label in target_gr_types:
                            # add a child gr if it's the right gr label
                            if g2.label in gr_types_to_child and reduce_pos(g2.arg[DEP].pos, g2.label) in gr_types_to_child[g2.label]:
                                for g3 in sent_grs:
                                    if g2.arg[DEP].index == g3.arg[HED].index:
                                        g2.add_child(g3)
                            #now add the gr to the verb instance
                            vi.add_gr(g2)
            sent_scfs = s.build_scfs()
            numvi = numvi + len(sent_scfs)
            for scf in sent_scfs: 
                self.lex.increment(scf)
### Uncomment next line to print the number of verb instances processed
#        print "Number of verb instances processed: " + str(numvi)


    def get_sentence(self):
        "modularizes for parser format"
        if parser_format == 'rasp':
            return self.rasp.read_one_sentence()
        elif parser_format == 'conll':
            return self.conll.read_one_sentence()


class CONLL:
    def __init__(self, filename):
        self.file = open(filename)

    def read_one_sentence(self):
        self.sentence_grs = []
        self.ids_lemmas = ["0"]
        self.ids_pos = ["0"]
        self.tmp_grs = []
        re_line = re.compile('(\d+)\t[^\t]+\t([^\t]+)\t[^\t]+\t([^\t]+)\t[^\t]+\t(\d+)\t([^\t]+)\t.*')
        while True:
            line = self.file.readline()
            line = line.strip()
            if re_line.search(line):
                id = re_line.sub('\\1', line)
                lemma = re_line.sub('\\2', line)
                pos = re_line.sub('\\3', line)
                head = re_line.sub('\\4', line)
                label = re_line.sub('\\5', line)
                self.ids_lemmas.append(lemma)
                self.ids_pos.append(pos)
                self.tmp_grs.append([label, head, lemma, id, pos])
            elif line == '':
                if not self.tmp_grs:
                    return "EOF"
                for tmpgr in self.tmp_grs:
                    label = tmpgr[0]
                    hlemma = self.ids_lemmas[int(tmpgr[1])]
                    hindex = tmpgr[1]
                    hpos = self.ids_pos[int(tmpgr[1])]
                    dlemma = tmpgr[2]
                    dindex = tmpgr[3]
                    dpos = tmpgr[4]
                    self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
                return self.sentence_grs
                                             
class RASP:
    def __init__(self, filename):
        self.file = open(filename)

    def read_one_sentence(self):
        self.sentence_grs = []
        re_sentence1 = re.compile('; \(\-[\d\.]+\)')
        re_sentence2 = re.compile('; \(\)\s*$')
        re_gr1 = re.compile('\(\|(\S+)\| \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\|\)')
        re_gr2 = re.compile('\(\|(\S+)\| _ \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\|\)')
        re_gr3 = re.compile('\(\|(\S+)\| \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\| _\)')   
        re_gr4 = re.compile('\(\|(\S+)\| \|(\S+):\S+\| \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\|\)')
        re_gr5 = re.compile('\(\|(\S+)\| \|(\S+)\| \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\|\)') 
        re_gr6 = re.compile('\(\|(\S+)\| \|(\S+):(\S+)_(\S+)\|\)')   # unary (passive)
        re_gr7 = re.compile('\(\|(\S+)\| \|(\S+):(\S+)_(\S+)\| \|(\S+):(\S+)_(\S+)\| \|(\S+)\|\)') 
        re_morphology = re.compile('(.*)\+[^\+]*$')
        expect_sent = True
        expect_divider = False
        expect_second_newline = False
        while True:
            line = self.file.readline()
            if not line:
                if self.sentence_grs:
                    return self.sentence_grs
                else:
                    return "EOF"
            line = line.strip()
            if re_sentence1.search(line) or re_sentence2.search(line):
                if not expect_sent:
                    raise Exception('Not expecting sentence')
                expect_sent = False
                expect_divider = True
                continue
            elif line == "gr-list: 1":
                if not expect_divider:
                    raise Exception('Not expecting divider')
                expect_divider = False
                continue
            elif line == '':
                if not expect_second_newline:
                    expect_second_newline = True
                    continue
                elif expect_second_newline:
                    return self.sentence_grs
            elif re_gr1.search(line):
                label = re_gr1.sub('\\1', line)
                hlemma = re_gr1.sub('\\2', line)
                hindex = re_gr1.sub('\\3', line)
                hpos = re_gr1.sub('\\4', line)
                dlemma = re_gr1.sub('\\5', line)
                dindex = re_gr1.sub('\\6', line)
                dpos = re_gr1.sub('\\7', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
            elif re_gr2.search(line):
                label = re_gr2.sub('\\1', line) + "_"
                hlemma = re_gr2.sub('\\2', line)
                hindex = re_gr2.sub('\\3', line)
                hpos = re_gr2.sub('\\4', line)
                dlemma = re_gr2.sub('\\5', line)
                dindex = re_gr2.sub('\\6', line)
                dpos = re_gr2.sub('\\7', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
            elif re_gr3.search(line):
                label = re_gr3.sub('\\1', line) + "_"
                hlemma = re_gr3.sub('\\2', line)
                hindex = re_gr3.sub('\\3', line)
                hpos = re_gr3.sub('\\4', line)
                dlemma = re_gr3.sub('\\5', line)
                dindex = re_gr3.sub('\\6', line)
                dpos = re_gr3.sub('\\7', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
            elif re_gr4.search(line):
                label = re_gr4.sub('\\1', line) + re_gr4.sub('\\2', line)
                hlemma = re_gr4.sub('\\3', line)
                hindex = re_gr4.sub('\\4', line)
                hpos = re_gr4.sub('\\5', line)
                dlemma = re_gr4.sub('\\6', line)
                dindex = re_gr4.sub('\\7', line)
                dpos = re_gr4.sub('\\8', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
            elif re_gr5.search(line):
                label = re_gr5.sub('\\1', line) + re_gr5.sub('\\2', line)
                hlemma = re_gr5.sub('\\3', line)
                hindex = re_gr5.sub('\\4', line)
                hpos = re_gr5.sub('\\5', line)
                dlemma = re_gr5.sub('\\6', line)
                dindex = re_gr5.sub('\\7', line)
                dpos = re_gr5.sub('\\8', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
            elif re_gr6.search(line):
                label = re_gr6.sub('\\1', line)
                hlemma = re_gr6.sub('\\2', line)
                hindex = re_gr6.sub('\\3', line)
                hpos = re_gr6.sub('\\4', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word("", 0, "")]))
            elif re_gr7.search(line):
                label = re_gr7.sub('\\1', line) + re_gr7.sub('\\8', line)
                hlemma = re_gr7.sub('\\2', line)
                hindex = re_gr7.sub('\\3', line)
                hpos = re_gr7.sub('\\4', line)
                dlemma = re_gr7.sub('\\5', line)
                dindex = re_gr7.sub('\\6', line)
                dpos = re_gr7.sub('\\7', line)
                if re_morphology.match(hlemma):
                    hlemma = re_morphology.sub('\\1', hlemma)
                if re_morphology.match(dlemma):
                    dlemma = re_morphology.sub('\\1', dlemma)
                self.sentence_grs.append(GR([label, Word(hlemma, hindex, hpos), Word(dlemma, dindex, dpos)]))
#            else:
#                raise Exception('Unexpected line format')
# too many rasp output bugs at the moment

class LexiconBuilder:
    "builds lexicon"
    def __init__(self):
        self.lex = Lexicon()
        im = InputManager(parser_output, self.lex)
        im.read_input()
        self.lex.calc_rel_freqs()

    def output_lexicon(self, thresh):
        self.lex.output(thresh)

lb = LexiconBuilder()
lb.output_lexicon(thresh)

