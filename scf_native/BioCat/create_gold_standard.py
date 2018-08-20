try:
    import lxml.etree as et
except:
    import xml.etree.ElementTree as et
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input")
parser.add_argument("-o", "--output", dest="output")
parser.add_argument("-a", "--annotators", dest="annotators", action="append", default=[])
parser.add_argument("-v", "--verbs", dest="verbs", action="append", default=[])
parser.add_argument("-f", "--filter", dest="filter", type=int)
parser.add_argument("-l", "--limit", dest="limit", action="store_true", default=False)
parser.add_argument("-r", "--removed", dest="removed")
options = parser.parse_args()


if options.removed:
    lrem = [l.split()[0].split(":") for l in open(options.removed)]


mapping = {
    "104" : "109",
    "141" : "38",
    "144" : "38",
    "161" : "51",
    "119" : "78",
    "108" : "12",
    "120" : "77",
    "127" : "78",
    "118" : "49",
    }

hrem = [107, 18, 33, 39, 40, 56, 58]

data = {}
xml = et.parse(options.input)
for verb in xml.getiterator("verb"):
    lemma = verb.get("lemma").replace("(s|z)", "z")    
    data[lemma] = {}
    if len(options.verbs) > 0 and lemma not in options.verbs:
        continue
    for inst in verb.getiterator("instance"):
        anns = len([x for x in inst.getiterator("scf") if x.text and x.text.isdigit()])
        skip = False
        for ann in inst.getiterator("annotation"):
            scf = [x for x in ann.getiterator("scf")][0].text
            if ann.get("name") == "semantic" and options.removed and [lemma, scf] in lrem:
                skip = True
        if skip:
            continue
        for ann in inst.getiterator("annotation"):
            name = ann.get("name")
            if len(options.annotators) > 0 and name not in options.annotators:
                continue
            scf = [x for x in ann.getiterator("scf")][0].text
            for f, t in mapping.iteritems():
                if scf == f:
                    scf = t
            if scf and scf.isdigit() and (not options.limit or anns == 2):
                data[lemma][scf] = data[lemma].get(scf, 0) + 1
                

if options.filter:
    for verb in data.keys():
        for scf in data[verb].keys():
            if data[verb][scf] <= options.filter:
                data[verb][scf] = 0

ttotal = 0
fd = open(options.output, "w")
for verb, scfs in data.iteritems():
    total = sum(scfs.values())
    ttotal += total
    if total == 0:
        continue
    fd.write("%s\n\n" % verb)
    for scf, count in scfs.iteritems():
        if count > 0:
            fd.write("%s %f\n" % (scf, float(count) / total))
    fd.write("\n")

