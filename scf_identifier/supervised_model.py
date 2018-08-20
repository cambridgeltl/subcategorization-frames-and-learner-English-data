from __future__ import division
from sklearn import linear_model, model_selection 
from sklearn.metrics import f1_score
from sklearn.feature_extraction import DictVectorizer
from scipy.sparse import csr_matrix, hstack, vstack
from nltk.util import ngrams as nltkngrams
import cPickle as pickle
import gensim
import codecs
import numpy as np
import copy
import re


def read_data(data_file):
  f = open(data_file, 'rb')
  data = pickle.load(f)
  f.close()
  return data

def readVectors(path, vecformat, cut = None):
    if vecformat == 'w2v':
        return gensim.models.Word2Vec.load_word2vec_format(path, binary = True, unicode_errors = 'ignore')
    elif vecformat == 'plaintext':
        m = {}
        f = open(path, 'r')
        for line in f:
            parts = line.rstrip().split()
            if cut: m[parts[0][:-cut]] = np.array([float(x) for x in parts[1:]])
            else: m[parts[0]] = np.array([float(x) for x in parts[1:]])

        f.close()
        return m

def normalize(token):
  penn_tokens = {
    '-LRB-': '(',
    '-RRB-': ')',
    '-LSB-': '[',
    '-RSB-': ']',
    '-LCB-': '{',
    '-RCB-': '}' 
  }

  if token in penn_tokens:
    return penn_tokens[token]

  token = token.lower()
  try:
    int(token)
    return "<NUM>"
  except:
    pass
  try:
    float(token.replace(',',''))
    return "<FLOAT>"
  except:
    pass
  return token


def extract_children_ids(word_pos_head_dep, word_id): 
  children_ids = []
  for wphd in word_pos_head_dep:
    if wphd['h'] == word_id:
      children_ids.append(wphd['i'])
  return children_ids

def full_children_attachment_check(word_pos_head_dep, word_id, processing_id):
  children_ids = extract_children_ids(word_pos_head_dep, word_id)
  for i in children_ids:
    if i >= processing_id:
      return False
  return True

def oracle_transition(word_pos_head_dep):
  # arc-standard: left-to-right, bottom-up processing
  stack = []
  arc = []
  reduce_record = []
  i = 0
  while len(reduce_record) < len(word_pos_head_dep):
    if i < len(word_pos_head_dep):
      wphd = word_pos_head_dep[i]

    if len(stack) > 1 and stack[-2]['h'] == stack[-1]['i'] and full_children_attachment_check(word_pos_head_dep, stack[-2]['i'], wphd['i']):
      head_to_remain = stack.pop()
      reduce_record.append(stack.pop())
      stack.append(head_to_remain)
    elif len(stack) > 1 and stack[-1]['h'] == stack[-2]['i'] and full_children_attachment_check(word_pos_head_dep, stack[-1]['i'], wphd['i']):
      reduce_record.append(stack.pop())
    else:
      if i < len(word_pos_head_dep):
        stack.append(wphd)
	i += 1
      else:
        reduce_record.append(stack.pop())
  return reduce_record

def serial_transition(oracle_word_pos_head_dep):
  serial_word_pos_head_dep = sorted(oracle_word_pos_head_dep, key = lambda x: x['i'])

  return serial_word_pos_head_dep

def head_from_oracle(oracle_word_pos_head_dep, w_index): # return None for ROOT
  owphd = oracle_word_pos_head_dep
  wphd_i = 0
  for wphd in owphd:
    if owphd[w_index]['h'] == wphd['i']:
      return wphd_i
    wphd_i += 1

def in_path(oracle_word_pos_head_dep, target_index, w_index, *deps):
  owphd = oracle_word_pos_head_dep
  while w_index != target_index and owphd[w_index]['d'] not in deps:
    w_index = head_from_oracle(owphd, w_index)
  
  if w_index != target_index and owphd[w_index]['d'] in deps:
    return True
  else:
    return False

def find_predecessor_wphd_by_dep(oracle_word_pos_head_dep, w_index, dep):
  owphd = oracle_word_pos_head_dep
  while owphd[w_index]['d'] != dep:
    w_index = head_from_oracle(owphd, w_index)
  return owphd[w_index]

def select_great_grand_child(oracle_word_pos_head_dep, target_index, w_index):
  owphd = oracle_word_pos_head_dep
  if owphd[w_index]['i'] >= owphd[head_from_oracle(owphd, w_index)]['i'] or not (re.search('^W', owphd[w_index]['p']) or owphd[w_index]['w'] in ['whether', 'if']):
    return False
  else:
    return True

def get_ngrams(string, n_min, n_max):
  string_ar = string.split()
  ng_list = []
  for n in range(n_min, n_max + 1):
    ng_list.extend(list(nltkngrams(string_ar, n)))
  return ng_list

def extract_feature(**param):
  instances = param['instances']

  # Get word embeddings if required
  if 'word_embedding' in param['feature']:
    word_embedding_model = readVectors(param['word_embedding_file'], 'plaintext')
    vocabulary = word_embedding_model.keys()
    word_embedding_dimension = len(word_embedding_model['word'])

    for ii, inst in enumerate(instances):
      stc_length = len(inst['stc_words'])
      target_position = inst['target_position']
      wsl = param['word_embedding_window_size_left']
      bi = max(0, target_position - wsl) 
      wsr = param['word_embedding_window_size_right']
      ei = min(stc_length - 1, target_position + wsr)

      word_embeddings = np.zeros((wsl + wsr + 1, word_embedding_dimension))
      for wei in range(bi, ei + 1):
	we_temp = word_embedding_model.get(inst['stc_words'][wei])
	if we_temp is not None:
	  word_embeddings[wei - target_position + wsl] = we_temp

      instances[ii]['word_embedding'] = np.concatenate(word_embeddings)

  # Get dependency dictionary if required
  if 'dep' in param['feature']:    
    for ii, inst in enumerate(instances):
      word_pos_head_dep = []

      # Collect dependency info of an instance
      for stc_wi in range(len(inst['stc_words'])):
        word_pos_head_dep.append({'i' : stc_wi + 1, 'w' : normalize(inst['stc_words'][stc_wi].lower()), 'p' : inst['stc_pos'][stc_wi], 'h' : inst['stc_head'][stc_wi], 'd' : inst['stc_dep'][stc_wi]})

      target_position = inst['target_position']

      wphd_stc_length = len(word_pos_head_dep)
      wphd_target_position = target_position

      # Change word_pos_head_dep to the oracle order for convenient search by dependency relation
      serial_wphd_target_position = wphd_target_position
      target_wphd = word_pos_head_dep[wphd_target_position]
      owphd = oracle_transition(word_pos_head_dep)
      for wphd_i in range(len(owphd)):
	if target_wphd == owphd[wphd_i]:
	  oracle_target_position = wphd_i
	  break

      word_pos_head_dep = owphd 
      wphd_target_position = oracle_target_position

      if 'ngram_dict' not in inst:
	instances[ii]['ngram_dict'] = {}

      # Add children's and grandchildren's features
      child_ids = []

      for w_index, wphd in enumerate(word_pos_head_dep):
	if wphd['h'] == target_wphd['i']:
	  child_ids.append(w_index)
	  child_feature = []
	  child_feature.append('dep_ch_%s' % wphd['d'])
	  child_feature.append('dep_ch_%s' % wphd['p'])
	  child_feature.append('dep_ch_%s' % wphd['w'])
	  child_feature.append('dep_ch_%s_%s' % (wphd['p'], wphd['d']))
	  child_feature.append('dep_ch_%s_%s' % (wphd['d'], wphd['w']))
	  child_feature.append('dep_ch_%s_%s_%s' % (wphd['p'], wphd['d'], wphd['w']))

	  for cf in child_feature:
	    if cf not in instances[ii]['ngram_dict']:
	      instances[ii]['ngram_dict'][cf] = 0
	    instances[ii]['ngram_dict'][cf] += 1


      grand_child_ids = [] 

      for cid in child_ids:
	for w_index, wphd in enumerate(word_pos_head_dep):
	  if wphd['h'] == word_pos_head_dep[cid]['i']: 
	    grand_child_ids.append(w_index)
	    grandchild_feature = []
	    grandchild_feature.append('dep_gch_%s' % (word_pos_head_dep[cid]['d']))
	    grandchild_feature.append('dep_gc_%s' % (wphd['d']))
	    grandchild_feature.append('dep_gc_%s' % (wphd['p']))
	    grandchild_feature.append('dep_gc_%s' % (wphd['w']))
	    grandchild_feature.append('dep_gc_%s_%s' % (word_pos_head_dep[cid]['d'], wphd['d']))
	    grandchild_feature.append('dep_gc_%s_%s' % (word_pos_head_dep[cid]['d'], wphd['p']))
	    grandchild_feature.append('dep_gc_%s_%s' % (word_pos_head_dep[cid]['d'], wphd['w']))
	    grandchild_feature.append('dep_gc_%s_%s_%s_%s' % (word_pos_head_dep[cid]['d'], wphd['p'], wphd['d'], wphd['w']))
	    for gc in grandchild_feature:
	      if gc not in instances[ii]['ngram_dict']:
		instances[ii]['ngram_dict'][gc] = 0
	      instances[ii]['ngram_dict'][gc] += 1
      
      for gcid in grand_child_ids:
	for w_index, wphd in enumerate(word_pos_head_dep):
	  if wphd['h'] == word_pos_head_dep[gcid]['i'] and select_great_grand_child(word_pos_head_dep, wphd_target_position, w_index):
	    great_grandchild_feature = []
	    great_grandchild_feature.append('dep_ggc_%s' % (wphd['d']))
	    great_grandchild_feature.append('dep_ggc_%s' % (wphd['p']))
	    great_grandchild_feature.append('dep_ggc_%s' % (wphd['w']))
	    great_grandchild_feature.append('dep_ggc_%s_%s' % (word_pos_head_dep[gcid]['d'], wphd['d']))
	    great_grandchild_feature.append('dep_ggc_%s_%s' % (word_pos_head_dep[gcid]['d'], wphd['p']))
	    great_grandchild_feature.append('dep_ggc_%s_%s' % (word_pos_head_dep[gcid]['d'], wphd['w']))
	    great_grandchild_feature.append('dep_ggc_%s_%s_%s_%s' % (word_pos_head_dep[gcid]['d'], wphd['p'], wphd['d'], wphd['w']))
	    for ggc in great_grandchild_feature:
	      if ggc not in instances[ii]['ngram_dict']:
		instances[ii]['ngram_dict'][ggc] = 0
	      instances[ii]['ngram_dict'][ggc] += 1

      # Add parent's and grandparent's features
      if target_wphd['h'] != 0:
	p_index = head_from_oracle(owphd, wphd_target_position)
	p_wphd = word_pos_head_dep[p_index]
	parent_feature = 'dep_pt_%s_%s_%s' % (p_wphd['p'], p_wphd['d'], p_wphd['w']) 
	instances[ii]['ngram_dict'][parent_feature] = 1
	if p_wphd['h'] != 0:
	  gp_wphd = word_pos_head_dep[head_from_oracle(owphd, p_index)]
	  grandparent_feature = 'dep_gpt_%s_%s_%s' % (gp_wphd['p'], gp_wphd['d'], gp_wphd['w']) 
	  instances[ii]['ngram_dict'][grandparent_feature] = 1
       
      
      # Add target verb's features
      instances[ii]['ngram_dict']['dep_tg_%s' % (target_wphd['p'])] = 1
      instances[ii]['ngram_dict']['dep_tg_%s' % (target_wphd['d'])] = 1
      
      # Add siblings' features
      if target_wphd['h'] != 0:
	p_index = head_from_oracle(owphd, wphd_target_position)
	p_wphd = word_pos_head_dep[p_index]
	for w_index, wphd in enumerate(word_pos_head_dep):
	  if wphd['h'] == p_wphd['i'] and wphd != target_wphd:
	    sibling_feature = 'dep_sb_%s_%s_%s' % (wphd['p'], wphd['d'], wphd['w'])
	    if sibling_feature not in instances[ii]['ngram_dict']:
	      instances[ii]['ngram_dict'][sibling_feature] = 0
	    instances[ii]['ngram_dict'][sibling_feature] += 1
      
       
      # Add dep ngrams 
      word_pos_head_dep = serial_transition(word_pos_head_dep)
      wphd_target_position = serial_wphd_target_position

      wsl = param['dep_window_size_left']
      bi = max(0, wphd_target_position - wsl)
      wsr = param['dep_window_size_right']
      ei = min(wphd_stc_length - 1, wphd_target_position + wsr)
      temp_wphd = np.array(word_pos_head_dep)[bi : ei + 1]

      dep_text = {'dl': '', 'du': ''}
      for wphd in temp_wphd:
	if len(dep_text['dl']):
	  dep_text['dl'] += ' '
	if len(dep_text['du']):
	  dep_text['du'] += ' '
	dep_text['du'] += '%s_%s' % (str(int(wphd['i']) - 1 - wphd_target_position), wphd['d'])
	dep_text['dl'] += '%s_%s' % (wphd['d'], wphd['w']) 

      for dt_type in dep_text:
       dep_ngram_temp = get_ngrams(dep_text[dt_type], param['dep_ngram_range'][0], param['dep_ngram_range'][1])            
       for dng in dep_ngram_temp:
	 dng_feat = dt_type + ' ' + ' '.join(dng)
	 if dng_feat not in instances[ii]['ngram_dict']:
	   instances[ii]['ngram_dict'][dng_feat] = 0
	 instances[ii]['ngram_dict'][dng_feat] += 1
	   
  return instances
  
def get_feature_vector(**param): # Generate input and output vectors
  X, y, info = [], [], []

  X_sub = {'word_embedding': [], 'ngram': []}
  X_dict = []

  ngram_vectorizer = None

  instances = param['instances']
  for inst in instances:
    if param['mode'] == 'train':
      y.append(inst['coarse_scf']['sd'])

    X_sub['word_embedding'].append(inst['word_embedding'])
    X_dict.append(inst['ngram_dict'])
    info.append([inst['stc_words'][inst['target_position']], inst['target_position'], ' '.join(inst['stc_words']).encode('utf-8')])
  
  X_sub['word_embedding'] = csr_matrix(X_sub['word_embedding'])

  if 'ngram_vectorizer' in param and param['ngram_vectorizer'] is not None:
    ngram_vectorizer = param['ngram_vectorizer']  
  else:
    ngram_vectorizer = DictVectorizer()
    ngram_vectorizer.fit(X_dict)      
  X_sub['ngram'] = ngram_vectorizer.transform(X_dict)

  X = hstack((X_sub['word_embedding'], X_sub['ngram']))

  X, y, info = csr_matrix(X), np.array(y), np.array(info, dtype = 'S')

  return X, y, ngram_vectorizer, info

def scf_supervised(**param): # Train or predict

  complete_param = copy.deepcopy(param)

  if param['mode'] == 'predict':
    # Load classifier
    clf_param_file = param['clf-param']
    clf_param = read_data(clf_param_file)
    clf = clf_param['clf']
    complete_param['ngram_vectorizer'] = clf_param['ngram_vectorizer']

  complete_param['instances'] = extract_feature(**complete_param)
  X, y, vectorizer, info = get_feature_vector(**complete_param)

  if param['mode'] == 'predict':
    # Predict
    y_predict = clf.predict(X)

    # Write output
    scf_f = open('%s.scf' % (param['filename']), 'w')
    i = 0
    for inst in param['instances']:
      scf_f.write('%s\t%s\t%s\t%s\n' % (inst['verb'], y_predict[i], inst['target_position'], ' '.join(inst['stc_words']).encode('utf-8')))
      i += 1
    scf_f.close()

  elif param['mode'] == 'train':
    # Create a new classifier
    clf = linear_model.LogisticRegression(class_weight = 'balanced')  
    
    
    # Cross-validation 
    X_gen, y_gen = X[0:6133], y[0:6133]
    X_ef, y_ef = X[6133:], y[6133:]

    fold_num = 10
    kf = model_selection.KFold(n_splits = fold_num, shuffle = True, random_state = 0)
    scores, baseline_scores = [], []

    # Create record for calculating the precision and recall for each SCF type
    with open('ef_scf_types.txt') as stf:
      scf_stats = {}
      for l in stf:
	scf = l.strip()
	if scf not in scf_stats:
	  scf_stats[scf] = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}

    # Create record for scf confusion pairs
    scf_confusion = {}

   
    print '\n%s cross-validation:\n' % fold_num
    fold_i = 1
    for train_idx, test_idx in kf.split(X_ef):
      X_train, X_test = vstack((X_gen, X_ef[train_idx])), X_ef[test_idx]
      y_train, y_test = np.concatenate((y_gen, y_ef[train_idx]), axis = 0), y_ef[test_idx]

      clf.fit(X_train, y_train)

      y_predict = clf.predict(X_test)
      y_predict_baseline = ['dobj_N' for yt in y_test] 

      scores.append(f1_score(y_test, y_predict, average='micro'))
      baseline_scores.append(f1_score(y_test, y_predict_baseline, average='micro'))
      print fold_i, scores[-1]

      for i in range(len(y_test)):
	for scf in scf_stats:
	  if y_test[i] == scf:
	    if y_predict[i] == scf:
	      scf_stats[scf]['TP'] += 1
	    else:
	      scf_stats[scf]['FN'] += 1
	  else:
	    if y_predict[i] == scf:
	      scf_stats[scf]['FP'] += 1
	    else:
	      scf_stats[scf]['TN'] += 1 

        if y_predict[i] != y_test[i]:
	  scs = '%s %s' % (y_test[i], y_predict[i])
	  if scs not in scf_confusion:
	    scf_confusion[scs] = 0
	  scf_confusion[scs] += 1

      fold_i += 1

    accuracy = round(np.mean(scores), 4)
    baseline_accuracy = round(np.mean(baseline_scores), 4)
    print 'Avergage accuracy: %s\nBaseline: %s' % (accuracy, baseline_accuracy)
  
    print '\nF1, precision, recall, and true frequency for each SCF:\n'
    for scf in scf_stats:
      precision = scf_stats[scf]['TP'] / max((scf_stats[scf]['TP'] + scf_stats[scf]['FP']), 1)
      recall = scf_stats[scf]['TP'] / max((scf_stats[scf]['TP'] + scf_stats[scf]['FN']), 1)
      if precision + recall == 0:
	f1 = 0
      else:
	f1 = 2 * precision * recall / (precision + recall)
      
      scf_stats[scf] = [precision, recall, f1, scf_stats[scf]['TP'] + scf_stats[scf]['FN']]

    sorted_scfs = sorted(scf_stats.items(), key = lambda x: (x[1][2], x[1][3]), reverse = True)
    for sscf in sorted_scfs:
      print sscf[0], str(round(sscf[1][2], 3)), str(round(sscf[1][0], 3)), str(round(sscf[1][1], 3)), int(sscf[1][3]) 

    print '\nSCF confusion: %s\n' % sum(scf_confusion.values())
    sorted_scss = sorted(scf_confusion, key = scf_confusion.get, reverse = True)
    for scs in sorted_scss:
      print '%s\t%s' % (scs, scf_confusion[scs])
	  

    # Train the classifier on all data
    clf.fit(X, y)

    # Store classifier
    classifier_file = param['clf-param']
    f = open(classifier_file, 'wb')
    data_to_store = {'clf' : clf, 'ngram_vectorizer' : vectorizer}
    pickle.dump(data_to_store, f, -1)
    f.close()

