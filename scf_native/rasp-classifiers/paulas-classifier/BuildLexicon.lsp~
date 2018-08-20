;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; BuildLexicon.LSP 
;;;
;;; -- matches underspecified GR patterns (rules) against RASP's GR output
;;;            
;;; Instruction for usage:
;;;
;;; 1) from within REPL: 
;;;    i)   set *run-with-repl* to t
;;;    ii)  load .lsp file into lisp and run (gr-matcher)
;;;
;;; 2) creating and using an image: 
;;;    i)   change *image-exec-file-name* as appropriate;
;;;    ii)  load .lsp file and save image using:
;;;         (sb-ext:save-lisp-and-die *image-exec-file-name* :toplevel 'gr-matcher)
;;;    iii) image can be load into lisp or executed from the command line with:
;;;         /usr/local/bin/sbcl --core imagefile.dxl parsefile
;;;
;;; 3) creating and using an executable:
;;;    i)   change *image-exec-file-name* as appropriate; 
;;;    ii)  load .lsp file and create executable with:
;;;         (sb-ext:save-lisp-and-die *image-exec-file-name* 
;;;                                  :toplevel 'gr-matcher :exectuable t )
;;;    iii) execute from command line with:
;;;         ./imagefile.dxl parsefile
;;;
;;; 4) to combine into rasp executable:
;;;    i)   change *image-exec-file-name* as appropriate; 
;;;    ii)  set *run-within-rasp* to t;
;;;    iii) load this file on top of the gde
;;;         For increased efficiency read the rule files at time of compilation 
;;;         (see *rule-file-name* and read-rules below)
;;;    iv)  create new executable with:
;;;         (sb-ext:save-lisp-and-die *image-exec-file-name* :exectuable t )
;;;    v)   If using rasp.sh make sure to set:
;;;         (setq +analysis-tree-type+ 'lr1-parse-analysis-grs) and 
;;;         (setq +analysis-tree-print-fn+ 'find-matches) within rasp_parse.sh
;;;         and replace path to gde with the path to the new executable
;;;   
;;; Input file format is expected to be RASP GR output (multiple parses allowed)
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;(in-package #+sbcl common-lisp-user)
(in-package #+(or cltl2 x3j13 ansi-cl) common-lisp-user #-(or cltl2 x3j13 ansi-cl) 'user)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; File names and Settings...(see also LoadLexiconBuilder.lsp)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defparameter *image-exec-file-name* "BUILDLEXICON")

(defparameter *rule-file-name* "rule-verbs-lexicon")
;(defparameter *backoff1* "rule-verbs-cc-lexicon")
;(defparameter *backoff2* "rule-verbs-ncsubj-lexicon")
;(defparameter *backoff3* "rule-verbs-ncsubj-cc-lexicon")

(defparameter *input-file-name* "/Users/paula/TestSubcatCode/JuditaTestData/subcat.tag2.parse")
(defparameter *output-file-name* "/Users/paula/TestSubcatCode/paula_results/subcat.tag2.parse.verb-ordered")
;(defparameter *input-file-name* nil)
;(defparameter *output-file-name* nil)

(defparameter *run-within-repl* t)
(defparameter *run-within-rasp* nil)

(eval-when (:compile-toplevel)
  (declare (optimize (speed 3) (safety 1))))

(if *run-within-rasp* 
    ;; to run within rasp we need to specify that we contruct grs 
    ;; and then run this code instead of the usual print function
      (setq +analysis-tree-type+ 'lr1-parse-analysis-grs)
      (setq +analysis-tree-print-fn+ 'find-matches))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Printing options...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defparameter *print-rule-defined-output* t)
(defparameter *print-best-match* t)
(defparameter *print-rule-label* nil)
(defparameter *order-by-verb-and-class* t)
(defparameter *print-as-xml* t)
(defparameter *print-full-sentence* nil)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Parsing options...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defparameter *complete-parses-only* nil)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Global data-structures 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; *sentence-no* and *parse-no* store the number of current sentence/parse encounterd.
(defparameter *sentence-no* 0)
(defparameter *parse-no* 0)

;; *verb* stores a single verb you wish to extract frames for
(defparameter *verb* nil)

;; *verb-list* stores the list of verbs you wish to extract frames for
(defparameter *verb-list* nil)

;; *rule-structure* stores all rules
(defparameter *rule-structure* (make-hash-table :test 'equal))

;; *back-structure*'s store the backoff rules
(defparameter *backoff-structure1* (make-hash-table :test 'equal))
(defparameter *backoff-structure2* (make-hash-table :test 'equal))
(defparameter *backoff-structure3* (make-hash-table :test 'equal))

;; *verb-ordered-data* stores the output for printing by class
;; hash be filled when *order-by-verb-and-class* is set to true
(defparameter *verb-ordered-data* (make-hash-table :test 'equal))

;; *all-grs* stores the full list of grs for the current parse
(defparameter *all-grs* nil)

;; *sentence* stores the text of the sentence being matched
(defparameter *sentence* nil)

;; *match-found* flags whether a match is found for the sentence
(defparameter *match-found* nil)

;; *best-match* stores the best match details and whatever property makes it the best 
(defparameter *best-match* (list :property 0 :rule nil :used-grs nil :mapping nil))

;; *best-matches* stores a list of the best matchs whenever there is a tie for best
(defparameter *best-matches* nil)

;; *best-match-property* global for accumuating the best-match property
(defparameter *best-match-property* nil)

;; *s-output* s expression for storing lexicon output.
(defparameter *s-output* (list :sentence nil :file nil :line nil :parseno nil
			       :totalparses nil
			       :rulefile nil
			       :class nil :target nil :pos nil :position nil :passive nil 
			       :args nil :otherpatterns nil :otherarggrs nil)) 

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Data cleaning functions 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun remove-multiple-underscore (lex-element)
  ;; remove multiple underscores from lex-element leaving only the last
  (let ((num (count #\_ lex-element :test #'equalp)))
    (remove-if #'(lambda (x) (if (and (equal (string x) "_")
				      (> num 1))
				 (setf num (- num 1)) 
				 nil)) lex-element)))

(defun remove-multiple-colon (lex-element)
  ;; remove multiple colons from lex-element leaving only the last
  (let ((num (count #\_ lex-element :test #'equalp)))
    (remove-if #'(lambda (x) (if (and (equal (string x) ":")
				      (> num 1))
				 (setf num (- num 1)) 
				 nil)) lex-element)))

(defun clean-lex-element (lex-element)
  ;; this is an alternative to string searching from the end of the file
  (remove-multiple-colon (remove-multiple-underscore (string lex-element))))

(defun valid-lex-element (lex-element)
  ;; returns t if lex-element is not a lamdba term
  (not (listp lex-element)))
  
	
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Lexical element matching functions 
;;; --- in the following lex-element refers to something of the form 
;;; --- |lemma+morph:num_tag|
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun symbol-equal (lex-element value) 
  ;; if value is the symbol value of lex-element return t
  (if (valid-lex-element lex-element)
    (string-equal (string lex-element) value)))

(defun word-value (lex-element orth)
  ;; if orth is the word-value of lex-element return t
  (if (valid-lex-element lex-element)
      (eql (search (string-downcase (concatenate 'string orth ":"))
		   (string-downcase lex-element)) 0)))

(defun word-value-case-sensitive (lex-element orth)
  ;; if orth is the case sensitive word-value of lex-element return t
  (if (valid-lex-element lex-element)
      (eql (search (string (concatenate 'string orth ":"))
		   (string  lex-element)) 0)))

(defun get-lemma (lex-element)
  ;; get the lemma of a word
  (if (valid-lex-element lex-element) 
      (if (search "+" (string lex-element))
	  (subseq (string lex-element) 0 (search "+" (string lex-element)))
	  (subseq (string lex-element) 0 (search ":" (string lex-element) :from-end t)))))

(defun pos-value (lex-element tag)
  ;; if tag is the pos-value of lex-element return t
  (if (valid-lex-element lex-element)
      (let ((clean-upper-lex (string-upcase lex-element)))
       (equal (string-upcase (concatenate 'string "_" tag))
                 (subseq clean-upper-lex (search "_" clean-upper-lex :from-end t) (length clean-upper-lex))))))

(defun pos-start (lex-element tag)
  ;; if pos of lex-element begins with tag return t
  (if (valid-lex-element lex-element)
      (search (string-upcase (concatenate 'string "_" tag))
      (string-upcase lex-element) :from-end t)))

(defun pos-end (lex-element tag)
  ;; if pos of lex-element ends with tag return t 
  (if (valid-lex-element lex-element)
      (let ((tag-length (length tag))
	    (lex-element-length (length lex-element))) 
	(search (string-upcase tag)
		(string-upcase 
		 (subseq (string lex-element) (- lex-element-length tag-length))) :from-end t))))

(defun pos-infix (lex-element tag)
  ;; if tag occurs in the pos of lex-element return t
  (if (valid-lex-element lex-element)
      (search (string-upcase tag) 
              (string-upcase (subseq (string lex-element) 
				     (search "_" (string lex-element) :from-end t))) :from-end t)))

(defun get-lex-position (lex-element)
  ;; get position of the word in a sentence
  (if (valid-lex-element lex-element)
       (let ((position1 (search ":" (string lex-element) :from-end t))
             (position2 (search "_" (string lex-element) :from-end t)))
         (if (and position1 position2)
             (subseq  (string lex-element) 
                      (+ 1 position1) position2) "0"))"0"))

(defun get-word-pm (lex-element)
  ;; get the word plus its morphology 
  (if (valid-lex-element lex-element)
      (let ((position (search ":" (string lex-element) :from-end t)))
        (if position
            (subseq  (string lex-element) 0 position)
	    (string lex-element)))))

(defun get-tag (lex-element)
  ;; extract the pos marker from a lex-element
  (if (valid-lex-element lex-element)
      (let ((position (search "_" (string lex-element) :from-end t)))
        (if position
            (subseq (string lex-element) (+ 1 position))
	    (string lex-element)))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; GR hierarchy, definitions and subsumption functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defconstant +gr-hierarchy+ 
  `(:hierarchy ("dependant" ("ta") 
		       ("arg_mod" ("mod" ("ncmod" "xmod" "cmod" "pmod"))
				  ("arg" ("subj" ("ncsubj" "xsubj" "csubj"))
					 ("subj_dodj" ("subj" "dobj"))
					 ("comp" ("obj" ("dobj" "obj2" "iobj"))
						 ("pcomp")
						 ("clausal" ("xcomp" "ccomp")))))
		       ("det") ("aux") ("conj")) 
	  :rest ("passive")))

(defconstant +gr-information+
  ;; datastructure to provide fast access to GR details 
  ;; (get-gr-info '|gr-name| ':info) -> data
  ;; current gr-info-list description: (|gr-name| :head head-position) 
  (let ((head-positions
	 `((|aux| :head 1) (|det| :head 1) (|pmod| :head 1) (|ncsubj| :head 1) 
	   (|xsubj| :head 1) (|csubj| :head 1) (|dobj| :head 1) (|obj2| :head 1)
	   (|iobj| :head 1) (|pcomp| :head 1) (|subj| :head 1) (|subj_dobj| :head 1) 
	   (|comp| :head 1) (|obj| :head 1) (|clausal| :head 1) (|passive| :head 1)
	   (|conj| :head 1) (|ncmod| :head 2) (|xmod| :head 2) (|cmod| :head 2) 
	   (|xcomp| :head 2) (|ccomp| :head 2) (|ta| :head 2) (|dependent| :head 2) 
	   (|mod| :head 2) (|arg| :head 2) (|arg_mod| :head 2))) ;(|comp| :head 2)))
	(table (make-hash-table :test 'equal)))
    (mapcar #'(lambda (x) (setf (gethash (car x) table) (cdr x))) 
	    head-positions) table))
 
(defconstant +aliases+ 
  ;; datastructure that contains any aliases to be used in the rules
  (list (cons '|objs| '(|obj| |dobj| |obj2|))))

(defmacro get-gr-info (gr-name info)
  `(getf (gethash ,gr-name +gr-information+) ,info))

(defun not-leaves (tree)
  (if (listp tree)
      (dolist (branch tree)
	(let ((x (listp branch)))
	  (if x (return x))))))

(defun is-in-hierarchy (gr &optional (tree (getf +gr-hierarchy+ :hierarchy)))
  ;; returns the subtree from where gr is found
  (if (listp tree)
      (let ((subtree (member gr tree :test #'equal)))
	(if subtree
	    subtree
	    (dolist (branch tree)
	      (let ((x (is-in-hierarchy gr branch)))
		(if x (return x))))))))
			

(defun subsumesp (gr1 gr2 &optional (tree (getf +gr-hierarchy+ :hierarchy)))
  ;; returns t if gr1 subsumes (or is equal to) gr2  
  (if (equal gr1 gr2)
      (return-from subsumesp t)
      (let ((subtree (is-in-hierarchy (string gr1) tree)))
	(if (not-leaves subtree)
	    (let ((x (is-in-hierarchy (string gr2) subtree)))
	      (if (not-leaves x) x (car x)))
	    (return-from subsumesp nil)))))

(defun matchp (gr1 gr2)
  (if (equal gr1 gr2)
      (return-from matchp t)
      (if (search "+" (string gr1))
	  (subsumesp (remove #\+ (string gr1) :from-end t) gr2)
	  (if (assoc gr1 +aliases+)
	      (progn 
		(mapcar #'(lambda (x) (if (matchp x gr2)
					  (return-from matchp t)))
			(cdr (assoc gr1 +aliases+)))
		(return-from matchp nil))
	      (return-from matchp nil)))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; GR connectedness functions (i.e. functions used to find generic graphs)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun contains-lambda (gr)
  (if (< 0 (count-if #'listp gr))
      t
      nil))
		
(defun get-tail (gr)
  (nth (+ (get-gr-info (car gr) :head) 1) gr))

(defun get-head (gr)
  (nth (get-gr-info (car gr) :head) gr))

(defun var-lookup (var mapping)
  (cdr (assoc var mapping)))

(defun contain-var (var grs)
  ;; collect all grs containing var
  (remove-if-not #'(lambda (x) (member var x :test #'equal)) grs)) 

(defun with-var-at-hd (var grs)
  ;; collect all grs containing var in the head position
  (let ((connected-list (contain-var var grs)))
    (remove-if-not #'(lambda (x) (equal var (get-head x))) connected-list)))

(defun with-var-at-tail (var grs)
  ;; collect all grs containing var in the head position
  (let ((connected-list (contain-var var grs)))
    (remove-if-not #'(lambda (x) (equal var (get-tail x))) connected-list)))

(defun connected-to-tail (gr grs)
  ;; collect tail-to-head connections from gr
  (with-var-at-hd (get-tail gr) grs))

(defun reachable-grs (gr grs)
  ;; collect all reachable tail-to-head connections from gr
  (let ((one-level (connected-to-tail gr grs)))
    (append one-level 
	    (dolist (gr-at-level one-level)
	      (let ((x (reachable-grs gr-at-level 
				      (remove-if #'(lambda (x) (member x one-level :test #'equal)) grs))))
		(if x (return x)))))))

(defun reachable-from-hd-var (var grs)
  ;; collect all grs that are reachable from the set of gr with var at their head
  (let ((head-level (with-var-at-hd var grs)))
    (append head-level 
	    (dolist (gr-at-hd-level head-level)
	      (let ((x (reachable-grs gr-at-hd-level grs)))
		(if x (return x)))))))
		     
(defun get-arg-grs (input-grs)
  ;; collects the arg-grs from the input grs
  (let ((args-subtree (is-in-hierarchy "arg")))
     (remove-if-not #'(lambda (x) (or 
                                   (subsumesp "arg" (car x) args-subtree)
                                   (equal '|passive| (car x))
                                   (and (equal '|ncmod| (car x))
                                    (equal '|prt| (second x)))))
      input-grs)))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; GR set reduction functions (i.e. functions use to refine set of grs)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun restrict-to-tail-pos (pos grs)
  ;; keep only grs when their modifier is tagged with pos
  (remove-if-not #'(lambda (x) (pos-start (get-tail x) pos)) grs))

(defun remove-tail-pos (pos grs)
  ;; remove grs if their modifier is tagged with pos
  (remove-if #'(lambda (x) (pos-start (get-tail x) pos)) grs))

(defun restrict-to-types (types grs)
  ;; keep only specific gr as specified in types list
  (remove-if-not #'(lambda (x) (member (car x) types :test #'equal)) grs))

(defun remove-types (types grs)
  ;; remove specific grs as specified by types list
  (remove-if #'(lambda (x) (member (car x) types :test #'equal)) grs))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Rule based functions (used for constraining patterns in rule-file-name)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; interpretation 1: looks at fully connected graph from var
(defun strict (var patterns grs)
  ;; checks that the arg GRs used in the match are all and 
  ;; only the arg GRs connected to var
  (let ((all-connected-args (get-arg-grs (reachable-from-hd-var var grs)))
	(matched-connected-args (get-arg-grs (reachable-from-hd-var var patterns))))
    (dolist (arg all-connected-args)
       (let ((x (member arg matched-connected-args :test #'equal)))
	(if (not x) (return-from strict nil)))) t))

;; interpretation 2: looks at graph limited to those reachable from head var
(defun strict (var patterns grs)
  (let ((all-connected-args (get-arg-grs (with-var-at-hd var grs)))
	(matched-connected-args (get-arg-grs (with-var-at-hd var patterns))))
    (dolist (arg all-connected-args)
      (let ((x (member arg matched-connected-args :test #'equal)))
	(if (not x) (return-from strict nil)))) t))

(defun is-passive (var grs)
  ;; return t if gr is passive
  (dolist (x (restrict-to-types (list '|passive|) grs))
    (if (equal (string (get-head x)) (string var))
	(return-from is-passive T)
	NIL)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Word extraction from GRS 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun get-word-list (grs)
  ;; get a list of each unique lex-element within the set of grs
  (let ((word-list ()))
    (dolist (x grs)
      (let ((gr-head (get-head x))
	    (gr-tail (get-tail x)))
	(if (and (not (null gr-head)) (not (member gr-head word-list :test #'equal))) (push gr-head word-list))
	(if (and (not (null gr-tail)) (not (member gr-tail word-list :test #'equal))) (push gr-tail word-list))))
  word-list))


(defun order-words (word-list)
  ;; order a list of lex-elements by they lexical position in the sentence
  (sort word-list #'(lambda (x y)
		      (< (parse-integer (get-lex-position x))
			 (parse-integer (get-lex-position y))))))

(defun strip-words (word-list)
  ;; strip a list of lex-elements to return a list of lemma+morph
  (mapcar #'(lambda (x) (get-word-pm x)) word-list))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Specific graph extraction (for specialised rule defined output---see *rule-file-name*)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defmacro value-of (toprint &body var)
  `(list ,toprint ,@var))

(defun single (var grs)
  ;; return only those grs directly connected to var
  (with-var-at-hd var grs))

(defun connected (var grs)
  ;; return all those grs reachable from var
  (reachable-from-hd-var var grs))

(defmacro get-prep-phrase-head (prep grs)
  ;; return the modifier from the gr with lex-element prep at the head
  `(get-tail (car (with-var-at-hd ,prep ,grs))))

(defmacro get-modifier-phrase (var grs)
  ;; return the graph of grs connected to those having lex-element var at the head
  `(reachable-from-hd-var ,var ,grs))

(defmacro get-conjunctions (var grs)
  ;; return gr list of conjunctive relations with var at head
  `(restrict-to-types (list '|conj|) (with-var-at-hd ,var ,grs)))

(defmacro single-noun-compound (var grs &optional det-p)
  ;; return gr list of ncmod relations with var at head
  ;; if det-p included determiner relations
  ;; adjoining preposition is excluded
  `(remove-tail-pos "I"
		    (if ,det-p
			(restrict-to-types (list '|ncmod| '|det|)
					   (with-var-at-hd ,var ,grs))
			(restrict-to-types (list '|ncmod|)
					   (with-var-at-hd ,var ,grs)))))

(defun get-compound-grlist (var grs patterns &optional det-p)
  ;; get the grs associated with the noun compounds within conjunctions 
  (let ((gr-list (with-var-at-tail var patterns)))
    (if (pos-start var "C")
	(dolist (x (get-conjunctions var grs))
	  (push x gr-list)
	  (dolist (y (single-noun-compound (get-tail x) grs det-p))
	    (push y gr-list)))
	(dolist (x (single-noun-compound var grs det-p))
	  (push x gr-list))) gr-list))

(defun get-compound-wordlist (var grs patterns &optional det-p)
  ;; extract the word list for the noun compounds within conjunctions 
  (let ((gr-list (list (get-compound-grlist var grs patterns det-p))))
    (push (order-words (get-word-list (car gr-list))) gr-list)))

(defmacro noun-compound (var grs &optional det-p)
  ;; for use in rule-file-name
  ;; returns the words associated with noun compounds (including conjunctions)
  ;; set det-p to include determiners
  `(let ((gr-list (get-compound-grlist ,var ,grs ,det-p)))
     (let ((word-list (get-word-list gr-list)))
       (if (member ,var word-list :test #'equal)
	   (strip-words (order-words word-list))
	   (strip-words (order-words (push ,var word-list)))))))

(defmacro get-head-word (var grs)
  ;; for use in rule-file-name
  ;; returns the head or a list if there is a conjunction
  `(if (pos-value ,var "CC")
       (mapcar #'(lambda (x) (get-tail x))
	       (get-conjunctions ,var ,grs))
       (list ,var)))

(defun get-all-args (patterns grs)
  ;; places all the data relating to each gr in patterns (excluding passives) into a s-expression: 
  (mapcar #'(lambda (x)
	      (list :keyword (get-head-word (get-tail (getf x :pattern)) grs)
		    :words (order-words 
			    (get-word-list 
			     (cons (getf x :pattern) (getf x :connected))))
		    :grs x)) 
	  (mapcar #'(lambda (y)
			  (list :pattern y 
				:connected (remove y (get-modifier-phrase 
						      (get-tail y) grs))))
;		  (remove-if #'(lambda (x) (equal '|passive| (car x)))
			     patterns
                             ;)
                             )))


(defun get-lexicon-data (var patterns grs)
  ;; places all data relating to var into s-expression
  (let* ((connected-ps (with-var-at-hd var patterns))
	 (other-ps (remove-if #'(lambda (x) (member x connected-ps :test #'equal)) 
			      patterns))
	 (other-connected-arg-grs (remove-if #'(lambda (x) (or (member x connected-ps :test #'equal)
							       (member x other-ps :test #'equal)))
					     (get-arg-grs (with-var-at-hd var grs)))))
    (setf (getf *s-output* :target)(get-lemma var))
    (setf (getf *s-output* :pos) (get-tag var))
    (setf (getf *s-output* :position) (get-lex-position var))
    (setf (getf *s-output* :passive) (is-passive var grs))
    (setf (getf *s-output* :args) (get-all-args connected-ps grs))
    (setf (getf *s-output* :otherpatterns) (get-all-args other-ps grs))
    (setf (getf *s-output* :otherarggrs) (get-all-args other-connected-arg-grs grs))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Single GR matching functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun use-map (mapping under-spec-list)
  ;; assign values to variables as stored in the mapping
  (mapcar #'(lambda (x) 
	  (if (listp x)
	      (use-map mapping x)
	      (let ((map-value (assoc x mapping)))
		(if map-value
		    (cdr map-value)
		    x)))) under-spec-list))

(defun rough-matchp (input-gr expanded-gr)
  ;; matches a input-gr against a expanded-gr 
  ;; returns a boolean
  ;; bug? why do i need to check for listp?---because of lambdas in the output??
  (if (or (not (listp input-gr))
	  (contains-lambda input-gr)
	  (contains-lambda expanded-gr)
	  (not (matchp (car expanded-gr) (car input-gr))))  
      (return-from rough-matchp nil))
  (mapcar #'(lambda (x y)
	      (if (not (equal x y))
		  (if (not (search "?" (string y)))
		      (return-from rough-matchp nil)))) (cdr input-gr) (cdr expanded-gr)) t)
      
(defun update-mapping (input-gr expanded-gr mapping)
  ;; update the mapping with info from an input gr 
  ;; returns the new mapping
  (append (remove-if-not #'consp (mapcar #'(lambda (x y)
			      (if (not (equal x y))
				  (cons y x))) input-gr expanded-gr))
	  mapping))


(defun expand-grs (hash mapping &optional (exp-unexp-cons nil))
  ;; expand keys (gr-patterns) of current hash according to content of mapping
  ;; returns a list (expanded-gr unexpanded-gr)
  (maphash #'(lambda (unexpanded-key v)
	       (if (not (equal unexpanded-key 'matched-rules))
		   (let ((expanded-key (use-map mapping unexpanded-key)))
		     (push (cons expanded-key unexpanded-key) exp-unexp-cons)))) hash)
  exp-unexp-cons)
	   
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Selecting the best match
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun check-for-best (rule mapping used-grs)
 ;; compares the best match so far with the current match
 ;; comparision is of the the size of a *best-match-property* that 
 ;; is calculated for each match by your-best-match-function (several examples below)
 ;; check-for-best will only be called if (setf *print-best-match* t)
  (if (> *best-match-property* (getf *best-match* :property))
      ;; if match is better than previous matches replace them
      (progn 
	(setf *best-match* 
	      (list :property *best-match-property* :rule (copy-list rule) 
		    :mapping (copy-list mapping) :used-grs (copy-list used-grs)))
	(setf *best-matches* nil))
      (if (= *best-match-property* (getf *best-match* :property))
	  ;; if match is equal keep both
	  (progn
	    (if (not *best-matches*)
		(setf *best-matches* (push *best-match* *best-matches*)))
	    (setf *best-matches* 
		  (push (list :property *best-match-property* :rule (copy-list rule) 
			      :mapping (copy-list mapping) :used-grs (copy-list used-grs))
			*best-matches*))))))

;;; the your-best-match-function method defines how the
;;; *best-match-property* value is evaluated alter this method
;;; according to your criteria for a best-match

;;  (defun your-best-match-function (rule x)
;;    ;; for a best match based on output length 
;;    (if (listp x)
;;  	  (setf *best-match-property* (+ *best-match-property* (length x)))
;;  	  (setf *best-match-property* (+ *best-match-property* 1))))

(defun your-best-match-function (rule x)
  ;; for a best match based on number of grs matched
 (setf *best-match-property* (length (getf rule :patterns)))
  ;; increment for every comp type gr add 1 to the property value
  (mapcar #'(lambda (y) 
	      (if (search "comp" (string-downcase (car y)))
		  (setf *best-match-property* (+ *best-match-property* 1))))
	  (getf rule :patterns))
  ;; increment for every mod type gr add 1 to the property value
  (mapcar #'(lambda (y) 
	      (if (search "mod" (string-downcase (car y)))
		  (setf *best-match-property* (+ *best-match-property* 1))))
	  (getf rule :patterns)))

;; (defun your-best-match-function (rule x)
;;   ;; for a best match based on last match found
;;  (setf *best-match-property* (+ (getf *best-match* :property) 1)))


(defun update-best-match (rule x)
 ;; function to initialise *best-match-property* and call your-best-match-function
  (if (equal *best-match-property* nil)
      (setf *best-match-property* 0))
  (your-best-match-function rule x))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Collating match data
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun add-to-class-list (class-hash)
  ;; collates similar classes together 
  ;; a class is usually defined by the rule label 
  ;; (see rule-file-name and to-output)
  (let* ((class (getf *s-output* :class))
	 (previous (gethash class class-hash))
         (c-s-output (copy-list *s-output*)))
    (if previous
	(setf (gethash class class-hash) (push c-s-output previous))
	(setf (gethash class class-hash) (list c-s-output))))
  class-hash)

(defun add-to-verb-list ()
  ;; collates similar verbs together
  ;; will be called if (setf *order-by-verb-and-class* t)
  (let* ((verb (getf *s-output* :target))
	 (previous (gethash verb *verb-ordered-data*)))
    (if previous
	(setf (gethash verb *verb-ordered-data*) (add-to-class-list previous))
	(setf (gethash verb *verb-ordered-data*) 
	      (add-to-class-list  (make-hash-table :test 'equal))))))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Printing output
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun simple-print (x out-str)
  ;; print s-expression *s-output* to out-str
  (format out-str "~S" *s-output*))

(defun replace-string (lex-element to-replace replace-with)
  ;; replace a specific string with another
  (let* ((s-item (string lex-element))
	 (location (search to-replace s-item)))
    (if location
	(let ((a (concatenate 'string 
			      (subseq s-item 0 location) replace-with
			      (subseq s-item (+ (length to-replace) 
						location)))))
	  (replace-string a to-replace replace-with)) s-item)))

;(defun replace-string (lex-element to-replace replace-with)
;  lex-element)

(defun replace-brackets (lex-element)
  ;; replace angle brackets 
  (replace-string (replace-string lex-element "<" "&lt;") ">" "&gt;"))

(defun replace-quotes (lex-element)
  ;; replace quotations 
  (replace-string (replace-string lex-element "\"" "&quot;") "\'" "&apos;"))
		
(defun clean-xml-data (item)
  ;; clean xml data 
  ;; add here any substitutions you wish to use for illegal characters
  (if (valid-lex-element item)
   (progn
    (replace-string
     (replace-string 
      (replace-string 
       (replace-string item "&" "**AA**")
       "**AA**#" "&#")
      "**AA**" "&amp;")
     "<" "&lt;"))
   NIL
 ))
  
(defun print-word-xml (lex-element out-str)
  ;; print word element xml (see XML/Lexicon.DTD)
 (if (valid-lex-element lex-element) 
  (if (search "</w>" (string lex-element))
      ;; handel <w> tags input
      (progn 
	(format out-str "<w c2=\"~a\" ~a</w>~%"
		(let ((tag-and-closing-w (string (get-tag lex-element))))
		  (clean-xml-data (subseq tag-and-closing-w 0 
					  (search "<" tag-and-closing-w))))
		(subseq (clean-xml-data (get-word-pm lex-element)) 3)))
      (progn (format out-str "<w c2=\"~a\">~a</w>~%" 
		     (clean-xml-data (get-tag lex-element))
		     (clean-xml-data (get-word-pm lex-element)))))))

(defun print-gr-xml (gr out-str patternp)
  ;; print gr element xml (see XML/Lexicon.DTD)
  (format out-str "<gr pattern=\"~a\" type=\"~a\" subtype=\"~a\" head=\"~a\" mod=\"~a\"/>~%"
	  patternp 
	  (car gr) 
	  (if (equal (length gr) 4)
	      (if (equal (get-gr-info (car gr) :head) 2)
		  (second gr)
		  (fourth gr))
	      nil)
	  (clean-xml-data (get-head gr))
	  (clean-xml-data (get-tail gr))))

	
(defun print-graphs-xml (out-str graph-list attachedp patternp)
  ;; print the graph element (see XML/Lexicon.DTD)
   (dolist (x graph-list)
      (let* ((grs (getf x :grs))
	     (gr-type (car (getf grs :pattern))))
	(format out-str "<graph type=\"~a\" keyword-list=\"~a\" c2-list=\"~a\" full-lex-list=\"~a\" contains-target=\"~a\" contains-pattern=\"~a\">~%" 
		gr-type 
		(mapcar #'(lambda (y) (clean-xml-data (get-word-pm y))) (getf x :keyword))
		(mapcar #'(lambda (y) (clean-xml-data (get-tag y))) (getf x :keyword))
                (mapcar #'(lambda (y) (clean-xml-data y)) (getf x :keyword)) 
		attachedp
		patternp)
	(dolist (y (getf x :words))
	  (print-word-xml y out-str))
	(print-gr-xml (getf grs :pattern) out-str patternp)
	(dolist (z (getf grs :connected))
	  (print-gr-xml z out-str nil))
	(format out-str "</graph>~%"))))

(defun print-s-as-xml (out-str v k)
  ;; print output as XML (see XML/Lexicon.DTD)
  (dolist (slist v)
    ;; only output if target is non-empty
    (if (string-not-equal (clean-xml-data (getf slist :target)) "")
	(progn
	  (format out-str "<instance classnum=\"~a\" target=\"~a\" c2=\"~a\" position=\"~a\" passive=\"~a\" filename=\"~a\" lineno=\"~a\" parseno=\"~a\" totalparses=\"~a\" rulefile=\"~a\">~%"
		  k
		  (clean-xml-data (getf slist :target))
		  (clean-xml-data (getf slist :pos))
		  (clean-xml-data (getf slist :position))
		  (getf slist :passive) 
		  (clean-xml-data (getf slist :file))
		  (getf slist :line)
		  (getf slist :parseno)
		  (getf slist :totalparses)
		  (getf slist :rulefile))
	  (format out-str "<sentence>~{~a ~}</sentence>~%" 
		  (mapcar #'(lambda (x) (clean-xml-data x)) (getf slist :sentence)))
	  (print-graphs-xml out-str (getf slist :args) t t)
	  (print-graphs-xml out-str (getf slist :otherpatterns) NIL t)
	  (print-graphs-xml out-str (getf slist :otherarggrs) t NIL)
	  (format out-str "</instance>~%")))))
	    

(defun print-class-ordered-data (class-hash verb combined-freq out-str)
  ;; print data ordered by the class
  ;; will be called if (setf *order-by-verb-and-class* t)
  (maphash #'(lambda (k v)
	       (let* ((l (length v))
		      (rf (/ l combined-freq)))
		 (if (not *print-as-xml*)
		     (progn 
		       (format out-str "(:class ~a " k)
		       (format out-str ":total ~a " l)
		       (format out-str ":relfreq ~a~%" rf)
		       (format out-str "~a)~%" v))
		     (progn 
		       (format out-str 
			       "<class classnum=\"~a\" target=\"~a\" freq=\"~a\" relfreq=\"~a\">~%" 
			       k verb l rf)
		       (print-s-as-xml out-str v k)
		       (format out-str "</class>~%" )))))
	   class-hash))


(defun print-verb-ordered-data (out-str)
 ;; print data ordered by the verb
 ;; will be called if (setf *order-by-verb-and-class* t)
 (if *print-as-xml*
	(progn 
	  (format out-str "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>~%")
	  (format out-str "<!DOCTYPE Lexicon SYSTEM \"../XML/Lexicon.DTD\">~%")
	  (format out-str "<lexicon rule-file-name=\"~a\" backoff1=\"~a\" backoff2=\"~a\" backoff3=\"~a\">~%"
		  *rule-file-name*
		  *backoff1* *backoff2* *backoff3*))
	(format out-str "("))
 (maphash #'(lambda (k v)
	      (let ((combined-freq 0.0))
		(maphash #'(lambda (k1 v1)
			     (setf combined-freq (+ (length v1) combined-freq))) v)
		(if *print-as-xml*
		    (progn 
		      (format out-str "<entry target=\"~a\" total=\"~a\">~%"
			      k
			      combined-freq)
		      (print-class-ordered-data v k combined-freq out-str)
		      (format out-str "</entry>~%"))
		    (progn 
		      (format out-str "(:verb ~a " k)
		      (format out-str ":total ~a " combined-freq)
		      (print-class-ordered-data v k combined-freq out-str)
		      (format out-str ")"))))) *verb-ordered-data*)
 (if *print-as-xml*
     (format out-str "</lexicon>~%")
     (format out-str ")")))

(defun evaluate-for-best-or-print (rule x out-str)
  ;; evalute the output on some "best" criteria
  ;; when (setf *print-best-match* t) else print it
  (if *print-best-match* 
      (update-best-match rule x)
      (if *order-by-verb-and-class*
	  (add-to-verb-list)
	  (simple-print x out-str))))

(defun to-output (rule mapping used-grs out-str)
  ;; expands output according to mapping and add to output structure
  (setf *match-found* t)
  (setf *best-match-property* nil)
  (push (cons '?patterns used-grs) mapping)
  (push (cons '?grs *all-grs*) mapping)
  (setf (getf *s-output* :class) (getf rule :label))
  (if *print-rule-defined-output*
      (progn 
	(mapcar #'(lambda (output-line) 
		    (evaluate-for-best-or-print rule (eval output-line) out-str) 
		    (if (and (not *order-by-verb-and-class*)
			     (not *print-best-match*))(format out-str "~%")))
		(use-map mapping (getf rule :output)))
	(if *print-best-match* (check-for-best rule mapping used-grs)))))
   
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Rule structure traversal to find matches
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun is-valid-rule (rule mapping used-grs)
  ;; checks the constraints against the mapping
  (push (cons '?patterns used-grs) mapping)
  (push (cons '?grs *all-grs*) mapping)
  (if (eval (use-map mapping (getf rule :constraints)))
      (if *verb*
       (if (not (equal (get-lemma (cdr (assoc '?x mapping))) *verb*))
        (return-from is-valid-rule nil)
        t)
       (if *verb-list*
        (if (not (member (get-lemma (cdr (assoc '?x mapping))) *verb-list* :test #'equal))
         (return-from is-valid-rule nil)
         t)
        t))
      (return-from is-valid-rule nil)))

(defun explore-node (remaining-grs used-grs hash mapping out-str)
  (if (gethash 'matched-rules hash)
      (dolist (rule (gethash 'matched-rules hash))
	(if (is-valid-rule rule mapping used-grs)
	    ;; LAURA: THIS SETQ MAKES A DIFFERENCE
	    (progn
	      (setq *print-best-match* t)
	      (to-output rule mapping used-grs out-str))))
                                                          )
  (let ((expanded-nodes (expand-grs hash mapping)))
    (dolist (gr-cons expanded-nodes)
      (let ((ex-gr (car gr-cons)) 
	    (key-gr (cdr gr-cons)))
	(dolist (gr remaining-grs)
	  (if (rough-matchp gr ex-gr)
	      (let* ((copy-mapping (copy-list mapping))
		     (new-mapping (update-mapping gr ex-gr copy-mapping))
		     (new-grs (remove-if #'(lambda (x) (equal x gr)) remaining-grs :count 1))
		     (new-hash (gethash key-gr hash))
		     (new-used-grs (nconc (list gr) used-grs)))
		(explore-node new-grs new-used-grs new-hash new-mapping out-str))))))))

(defun print-best-match (out-str)
  (setf *print-best-match* nil)
  (if *best-matches* 
      (mapcar #'(lambda (x)
		  (to-output (getf x :rule) (getf x :mapping) 
			     (getf x :used-grs) out-str)) *best-matches*)
      (to-output (getf *best-match* :rule) (getf *best-match* :mapping) 
		 (getf *best-match* :used-grs) out-str))
  (if (not *order-by-verb-and-class*)(format out-str "~%"))
  (setf *print-best-match* t)
  (setf *best-match* (list :property 0 :rule nil :used-grs nil :mapping nil))
  (setf *best-matches* nil)
  (setf *best-match-property* nil))
  
;; todo: for neatness change process-grs-from-file so that the gr-list is (list gr-list)
(defun find-matches (n-best-parses out-str)
  (setf *parse-no* 0)
  (dolist (gr-list n-best-parses)
    (setf *parse-no* (+ *parse-no* 1))
    (setf (getf *s-output* :parseno) *parse-no*)
    (setf *all-grs* gr-list)
    (setf (getf *s-output* :rulefile)  "rule-file-name")
    (explore-node gr-list nil *rule-structure* nil out-str)
    (if (not *match-found*)
	(if *backoff1* 
	    (progn
	      (if (not *order-by-verb-and-class*)
		  (format out-str "backoff1!~%"))
	      (setf (getf *s-output* :rulefile)  "backoff1")
	      (explore-node gr-list nil *backoff-structure1* nil out-str))))
    (if (not *match-found*)
	(if *backoff2*
	    (progn 
	      (if (not *order-by-verb-and-class*)
		  (format out-str "backoff2!~%"))
	      (setf (getf *s-output* :rulefile)  "backoff2")
	      (explore-node gr-list nil *backoff-structure2* nil out-str))))
    (if (not *match-found*)
	(if *backoff3* 
	    (progn 
	      (if (not *order-by-verb-and-class*)
		  (format out-str "backoff3!~%"))
	      (setf (getf *s-output* :rulefile)  "backoff3")
	      (explore-node gr-list nil *backoff-structure3* nil out-str)))))
  (if (and (not *match-found*) (not *order-by-verb-and-class*))
      (format out-str "No Match Found!~%"))
  (if *print-best-match* (print-best-match out-str))
  (setf *match-found* nil))
    
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Processing GRs from an input file
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun locate-sent-and-num (stream)
  (do* ((first-s-read (read stream nil) next-s-read)
	(next-s-read (read stream nil) (read stream nil)))
      ((or (not next-s-read)
	   (integerp next-s-read)) 
       (if (not next-s-read) 'eof (cons first-s-read next-s-read)))))

(defun get-gr-set (stream gr-set)
  (do* ((next-line (read stream nil) (read-from-string (read-line stream nil "") nil)))
       ((or (eql nil next-line)(equal next-line "")) gr-set)
    (push next-line gr-set))
  ;; could order here by gr frequency to make faster
  (nreverse gr-set))

(defun process-grs-from-file (in)
  (let ((out-str (if *output-file-name* 
		     (open *output-file-name* :direction :output 
			   :if-does-not-exist :create
			   :if-exists :supersede)
		     *standard-output*)))
    ;; add here with-open-file statement to print to output file
      (do* ((sent-and-num (locate-sent-and-num in) (locate-sent-and-num in)))
	   ((equal sent-and-num 'eof))
	(setf  *s-output* (list :sentence nil :file nil :line nil :parseno nil
				:totalparses nil
				:rulefile nil 
				:class nil :target nil :pos nil :position nil 
				:passive nil :args nil :otherpatterns nil :otherarggrs nil))
	(setf *sentence* sent-and-num)
        (setf *sentence-no* (+ *sentence-no* 1))
	(if (not (and (equal (cdr sent-and-num) 0) *complete-parses-only*))
	    (progn
	      (setf (getf *s-output* :sentence) 
		    (if *print-full-sentence*
			(car *sentence*)
			(strip-words (car *sentence*))))
	      (setf (getf *s-output* :totalparses) (cdr *sentence*))
	      (setf (getf *s-output* :file)  *input-file-name*)
	      (setf (getf *s-output* :line) *sentence-no*)
	      (let ((n-best-parses ()))
		(dotimes (x (let ((num (cdr sent-and-num)))
			      (if (> num 0) num 1)))
		  (push (get-gr-set in ()) n-best-parses))
		(find-matches (nreverse n-best-parses) out-str))))
	(if (not *order-by-verb-and-class*)(format out-str "~%")))))
;   (if *order-by-verb-and-class*
;      (print-verb-ordered-data out-str))
;   (if *output-file-name* (close out-str))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Main matching function
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defparameter *time1* nil)
(defparameter *time2* nil)

(defun gr-matcher ()
  (setf *time1* (get-internal-run-time))
  (setf *sentence-no* 0)
  ;; contains SBCL specfic sb-ext --- needs to be abstracted
  ;; e.g. for allegro use (sys:command-line-argument 0)
  ;; and for lispworks (nth 0 (io::io-get-command-line-arguments)))
  (if *input-file-name*
      (progn 
	(format t "Reading GRs from: ~S~%" *input-file-name*)
	(with-open-file 
	    (in *input-file-name* :direction :input :if-does-not-exist :error :external-format :iso-8859-1)
;;	    (in *input-file-name* :direction :input :if-does-not-exist :error :external-format :ascii)
	  (process-grs-from-file in))
	(if (not *run-within-repl*) (sb-ext:quit)))
      (if (<= (length sb-ext:*posix-argv*) 1)
	  (progn 
	    (process-grs-from-file *standard-input*)
	    (sb-ext:quit))
	  (let ((arguments (cdr sb-ext:*posix-argv*)))
	    (dolist (arg arguments) 
	      (with-open-file 
		  (in arg :direction :input :if-does-not-exist :error)
		;;(format t "Reading GRs from: ~S~%" arg)
		(process-grs-from-file in)))
	    (sb-ext:quit))))
  (setf *time2* (get-internal-run-time))
  (format t "Computation took:~%")
  (format t "  ~f seconds of run time~%"
	  (/ (- *time2* *time1*) internal-time-units-per-second)))
 

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Read in the rules
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun make-gr-freq-hash (rules)
  (let ((freq-hash (make-hash-table :test 'equal)))
    (dolist (rule rules)
      (let ((gr-pattern-list (car rule)))
	(dolist (gr-pattern gr-pattern-list)
	  (if (eql nil (gethash gr-pattern freq-hash))
	      (setf (gethash gr-pattern freq-hash) 1))
	  (setf (gethash gr-pattern freq-hash) 
	    (+ (gethash gr-pattern freq-hash) 1)))))
    freq-hash))

(defun make-rule-plist (rule)
  ;; to lable additional elements in rule structure edit here
  (list :patterns (first rule) :constraints (second rule) 
	:output  (third rule) :label (fourth rule)))

;; Todo: we don't need to pass the rule and the pattern-list...it's in the rule already!
(defun add-to-structure (pattern-list rule hash)
  (let ((pattern (car pattern-list)))
    (if (eql nil (gethash pattern hash))
	(let ((newtable (make-hash-table :test 'equal)))
	  (setf (gethash pattern hash) newtable)))
    (if (eql nil (cdr pattern-list))
	(if (eql nil (gethash 'matched-rules (gethash pattern hash)))
	    (setf (gethash 'matched-rules (gethash pattern hash)) 
	      (list rule))
	  (setf (gethash 'matched-rules (gethash pattern hash))
	    (push rule (gethash 'matched-rules (gethash pattern hash)))))
      (add-to-structure (cdr pattern-list) rule (gethash pattern hash)))))

;; function to print recursive hashes
;; not required in image
(defun phash (hash &optional (string ""))
  (maphash #'(lambda (k v)
	       (let ((string (concatenate 'string string "  ")))
		 (if (listp v) 
		     (progn
		       (format t "~%~a~a =>" string k)
		       (dolist (each v)
			 (format t "~a " (getf each :label))))
		   (progn (format t "~%~a~a => " string k) 
			  (phash v string))))) hash))

(defun build-rule-structure (rules structure-name)
  (let ((gr-freq-hash (make-gr-freq-hash rules)))
    (dolist (rule rules)
      (let ((rule (make-rule-plist rule)))
	(setf (getf rule :patterns) (stable-sort (getf rule :patterns)
	      #'(lambda (a b)
		  (> (gethash a gr-freq-hash) 
		     (gethash b gr-freq-hash)))))
	  (add-to-structure (getf rule :patterns) rule structure-name)))))
    
(defun read-rules (file-name structure-name)
  (with-open-file (in file-name :direction :input 
		   :if-does-not-exist :error)
    (format t "Reading rules in ~a..." file-name)
    (let ((all-rules (read in nil)))
      (build-rule-structure all-rules structure-name))))
 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Execution...(see LoadLexiconBuilder.lsp)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;(read-rules *rule-file-name* *rule-structure*)
;(read-rules *backoff1* *backoff-structure1*)
;(read-rules *backoff2* *backoff-structure2*)
;(read-rules *backoff3* *backoff-structure3*)

;; To excute on a specified file:
;(gr-matcher)
;; To save an image: 
;(sb-ext:save-lisp-and-die *image-exec-file-name* :toplevel 'gr-matcher)
;; To save an executable:
;(sb-ext:save-lisp-and-die *image-exec-file-name* :toplevel 'gr-matcher :executable t)

