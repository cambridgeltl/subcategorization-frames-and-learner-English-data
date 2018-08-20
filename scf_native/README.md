This directory contains subcategorization frame (SCF) resources for native English. There are four gold standards in the following domains: 

- general; 
- labor law; 
- environment;
- biomedicine.

There are also some scripts and auxiliary documents for the extraction and classification of SCFs, and for mapping between different SCF inventories. The distribution of the resources in this directory is as follows.


**1.  SCF annotation guideline**: 

`anno_guidelines_21Nov2012`



**2. Annotated data for the general, "labor law" and "environment" domains**:

Domains: `/annotated/domains`

General Language: `/annotated/genlg`

General language SCFs were annotated by Diane Nicholls in 2013.  Data comes from the BNC.

Annotations are in userfiles, and tasks (the sentences to be annotated) in taskfiles.  The sentence ID can be used to match up the annotation with the original sentence, if desired.



**3. Source data for the "labor law" and "environment" domains**:

The crawled data from the PANACEA project, which was used as the source for the annotated domain data, can be found in

`/monolingual_data`

There are two subdirectories, MCv1_IN_DOMAIN ("monolingual corpus") and augmented_data.  The PANACEA deliverables explain these two corpora.



**4. SCF resources for the biomedical domain**:

`/BioCat`

These are resources provided by Thomas Lippincott (Lippincott et al., 2013), see README inside the directory for detail.



**5. Typed-level SCF gold standards and the mapping between various fine-grained SCF inventories**:

`/gold`

(provided by Laura Rimell)


**6. Some scripts for processing SCFs**:

`/scripts`

Scripts provided by Laura Rimell for e.g., the extraction of typed-level SCFs, see README inside the directory for detail.


**7. RASP-based subcat classifier**:

For example, run the classifier for verbs using the command:

`sh runLexiconBuilder.sh -i <input rasp parsed output> -o <output file>`

For nouns, use "runLexiconBuilder_noun.sh"
For adjectives, use "runLexiconBuilder_adj.sh"


**8. SCF gold standards mapped to coarse-grained SCF inventory (based on stanford typed dependency)**:

`/coarse-grained`

The three datasets (gen.dat, lab.dat, env.dat) were generated by Yan Huang from the annotated data (No.2 in this list). Some manual correction has been made to the original annotation. The SCFs were mapped to a coarse-grained SCF inventory based on 'SCF_mapping_yan_201703.txt'. For details of the SCF inventory, please refer to the PhD thesis of Yan Huang (Automatic syntactic analysis of learner English).

One can use the cPickle module of python to load the datasets. The data structure of each dataset is as follows. The highest level structure is a python dictionary with verb lemmas as the keys. Each verb lemma entry includes a number of instances, with each instance being a dictionary containing sub-structures of the sentence ('stc_words'), the position of the target verb ('target_position'), the SCF of the target verb ('coarse-grained' -> 'sd') etc. For more detail of the data structure, please print the first instance of an verb lemma entry and inspect the example.



**References**:

Lippincott T., Rimell L, Johnson H., Verspoor K. and Korhonen A. (2013). Acquisition and evaluation of verb subcategorization resources for biomedicine. Journal of Biomedical Informatics. Volume 46, Issue 2. Pages 228-237. 

Quochi, V., Frontini, F., Bartolini, R., Hamon, O., Poch, M., Padró, M., Bel, N., Thurmair, G., Toral, A., and Kamram, A. (2014). Third evaluation report. Evaluation of PANACEA v3 and produced resources.