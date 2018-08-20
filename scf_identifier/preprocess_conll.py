import cPickle as pickle
import codecs

def extract_verb_instance(stc):
  instances = []

  for ti in range(len(stc['word'])):
    if ('V' in stc['pos'][ti]) and (stc['dep'][ti] not in ['nsubj', 'dobj', 'iobj', 'pobj', 'amod', 'acomp', 'prep', 'aux', 'auxpass']):
      instances.append({'target_position' : ti, 'verb': stc['word'][ti], 'stc_words' : stc['word'], 'stc_pos' : stc['pos'], 'stc_head': stc['head'], 'stc_dep': stc['dep']})
 
  return instances


def transform_conll(data_file):
  dat_dump = codecs.open(data_file + '.dmp', 'w')

  with codecs.open(data_file, encoding = 'utf-8') as f:
    instances = []
    stc = {'word': [], 'pos': [], 'head': [], 'dep': []}
    for l in f:
      if len(l.strip()) == 0:
	  instances += extract_verb_instance(stc)
	  stc = {'word': [], 'pos': [], 'head': [], 'dep': []}
      else:
	ar = l.strip().split('\t')
	stc['word'].append(ar[1])
	stc['pos'].append(ar[4])
	stc['head'].append(int(ar[6]))
	stc['dep'].append(ar[7])

      
  # Store the data
  pickle.dump(instances, dat_dump, -1)
  dat_dump.close()

  return instances
