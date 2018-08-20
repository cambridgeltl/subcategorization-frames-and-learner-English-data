from __future__ import division
import preprocess_conll as pc
import supervised_model as sm
import cPickle as pickle
import numpy as np
import sys
import copy
import os

# Set the parameters
param = {
  'feature' : ['dep', 'word_embedding'],
  'dep_window_size_left': 1,
  'dep_window_size_right': 3,
  'dep_ngram_range' : (1, 2),
  'word_embedding_file': 'counter-fitted-vectors.txt',
  'word_embedding_window_size_left' : 0,
  'word_embedding_window_size_right' : 0,
  'mode': 'predict', # 'train' or 'predict'
  'training_file': 'train.dat',
  'filename': 'test.txt',
  'clf-param': 'eng.clf-param'
}

# Get input
if param['mode'] == 'train':
  instances = sm.read_data(param['training_file']) 
elif param['mode'] == 'predict':
  if os.path.isfile(param['filename']):
    file_info = os.stat(param['filename'])
    file_size = file_info.st_size / 1024.0 / 1024.0
    if file_size > 30:
      print 'Error: Your file is larger than 30 MB. Please split it into smaller files and process them separately.'
      sys.exit()
  else:
    print 'Error: The file you set in \'filename\' cannot be found. Please check and set the right path.'
    sys.exit()
  instances = pc.transform_conll(param['filename'])

else:
  print 'Please set a feasible mode: \'train\' or \'predict\''
  exit
param['instances'] = instances

# Train or predict
sm.scf_supervised(**param)
