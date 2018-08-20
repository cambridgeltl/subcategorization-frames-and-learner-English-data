This subcategorization frame (SCF) identifier is intended to identify the SCFs of individual verbs occurrences in native or learner English text. For the linguistic and technical details about the SCF identifier, please refer to (Huang, 2018).


**Input format**:

The input file should contain the dependency structure of sentences in the [CoNLL-U format](http://universaldependencies.org/format.html). The dependency scheme is universal dependencies. Since the dependency structure of the training data and testing data for the SCF identifier was extracted by  SyntaxNet (version retrieved on April 26, 2017), for the best result please use the closest version of SyntaxNet to extract the dependency structure of the input sentences. An example of the dependency structure of a sentence from EF-Cambridge Open Language Database (EFCAMDAT) is as follows:

	ID	FORM	LEMMA	UPOS	XPOS	FEATS	HEAD	DEPREL	DEPS	MISC
	1	After	_	ADP	IN	_	10	prep	_	_
	2	some	_	DET	DT	_	3	det	_	_
	3	time	_	NOUN	NN	_	1	pobj	_	_
	4	,	_	.	,	_	10	punct	_	_
	5	the	_	DET	DT	_	6	det	_	_
	6	affection	_	NOUN	NN	_	10	nsubj	_	_
	7	between _	ADP	IN	_	6	prep	_	_
	8	them	_	PRON	PRP	_	7	pobj	_	_
	9	is	_	VERB	VBZ	_	10	aux	_	_
	10	progressing	_	VERB	VBG	_	0	ROOT	_	_
	11	well	_	ADV	RB	_	10	advmod	_	_
	12	.	_	.	.	_	0	ROOT	_	_



**Output format**:

The output file is named by adding a file extension of '.scf' to the input file. Each line in the output file shows the SCF of a verb, with four tab-separated columns denoting the verb, the SCF, the position of the verb in the sentence, and the sentence respectively. For example, the output for the example sentence above is: 

	Verb		SCF	Position	Sentence
	progressing	advmod	9		After some time , the affection between them is progressing well .


**How to use the identifier**:

1. Enter the directory of the identifier;
2. Unzip the word embedding file "counter-fitted-vectors.zip";
3. Set the parameters in ‘scf_identifier.py’:
  - To replicate the experiments in (Huang, 2018), please set the value of ‘mode’ to ‘train’;
  - To identify SCFs for your own text, please set the value of ‘mode’ to ‘predict’, and set the value of ‘filename’ to the path to your input file which contains the dependency structure of the sentences in your text. Note that if your file is too large (more than 30 MB), you should split the file into smaller ones and process them separately;
4. Run the identifier: `python scf_identifier.py`.


**Reference**:

Huang Y. (2018). Automatic syntactic analysis of learner English. PhD thesis. Language Technology Lab, Faculty of Modern and Medieval Languages, University of Cambridge.
