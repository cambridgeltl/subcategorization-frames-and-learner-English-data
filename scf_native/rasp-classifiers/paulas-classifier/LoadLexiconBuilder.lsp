;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; LoadLexiconBuilder.lsp 
;;; Author: Paula Buttery
;;; Loads rule files and uses them to extract syntactic patterns from data
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(load "BuildLexicon.lsp")
(setf *run-within-repl* t)
(setf *run-within-rasp* nil)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Rules
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Path to rule file and backoff rule files

(defparameter *rule-file-name* "rule-verbs-lexicon")
(defparameter *backoff1* "rule-verbs-cc-lexicon")
(defparameter *backoff2* "rule-verbs-ncsubj-lexicon")
(defparameter *backoff3* "rule-verbs-ncsubj-cc-lexicon")

;; Load in rule and backoff files 

(read-rules *rule-file-name* *rule-structure*)
(read-rules *backoff1* *backoff-structure1*)
(read-rules *backoff2* *backoff-structure2*)
(read-rules *backoff3* *backoff-structure3*)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; IO
;;; Input file format is expected to be RASP GR output (multiple parses allowed)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; IL: These 4 parameters need setting either manually by altering this file
;;     or through runLexiconBuilder.sh

;(defparameter *input-directory* "/Users/pjb48/TestSubcatCode/JuditatestData/old_183_parse/")
;(defparameter *output-directory* "/Users/pjb48/TestSubcatCode/paula_results/")

;; If input is from a single file then name it here
;; (it will be assumed to be located in the *input-directory*)

;(defparameter *input-file-short-name* "absorb.BNC-lemmatized")

;; If all output is to a single file then name it here
;; (it will be assumed to be located in the *output-directory*)

;(defparameter *output-file-short-name* "absorb.BNC-lemmatized.out")

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Printing options
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(setf *order-by-verb-and-class* t)
(setf *print-as-xml* t)
(setf *print-best-match* nil)
(setf *print-rule-label* nil)
(setf *print-full-sentence* t)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Parsing options...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(setf *complete-parses-only* nil)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Verbs
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; To find matches for verbs from a specified list

(setf *verb-list* nil)
;(setf *verb-list* '("seems" "matters"))


;; To find matches for specific verbs from specific files
;; format of list ((verb1 (filename1 filename2 ...))
;;                 (verb2 (filename 3...))
;;                 ...)
;; Files will be assumed to be located in the *input-directory*

(defparameter *verb-with-files-list* nil)
;(defparameter *verb-with-files-list*
; '(("absorb" 
;    ("absorb.NANT"))
;   ("annoy"
;    ("annoy.NANT"))))
  
;; alternatively load a lisp file that contains the *verb-with-files-list* datastructure
;(load "allverbs.lsp")

(defun get-verb-lexs ()
 (setf *verb-ordered-data* (make-hash-table :test 'equal))
 (if *verb-with-files-list*
  (dolist (x *verb-with-files-list*)
   (setf *verb* (car x))
   (setf *verb-ordered-data* (make-hash-table :test 'equal))
   (setf *output-file-name* (concatenate 'string *output-directory* *verb*))
   (let ((out-str (open *output-file-name* :direction :output 
                   :if-does-not-exist :create
                   :if-exists :supersede)))
    (dolist (y (second x))
     (setf *input-file-name* (concatenate 'string *input-directory* y))
     (gr-matcher))
    (if *order-by-verb-and-class*
     (print-verb-ordered-data out-str))
    (close out-str)))
  (progn
   (setf *output-file-name* (concatenate 'string *output-directory* *output-file-short-name*))
   (setf *input-file-name* (concatenate 'string *input-directory* *input-file-short-name*))
    (let ((out-str (open *output-file-name* :direction :output 
			   :if-does-not-exist :create
			   :if-exists :supersede)))
     (gr-matcher)
     (if *order-by-verb-and-class*
	 (print-verb-ordered-data out-str))
     (close out-str)))))
   
;; TOP-LEVEL CALL
; (made directly, or via runLexiconBuilder.sh)

;(get-verb-lexs)

