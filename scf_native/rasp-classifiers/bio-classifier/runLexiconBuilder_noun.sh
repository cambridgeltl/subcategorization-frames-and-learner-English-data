#!/bin/sh
#
# Ian Lewin Nov'07
#
# Usage: runLexiconBuilder.sh -i <file> -o <dir|file>  -v <verb> -d"
#
# Expects a file for -i (input)
# Expects a file for -o (output) only if no -v option is specified
# Expects a dir  for -o (output) only if the -v option is specified
#
# So, given an input file spec and an output file spec, generates one output file
# for all verbs in input file
#
# Given an input file spec, an output dir and a verb, generates output/verb for that verb
#
# 1. You must have sbcl on your path
# 2. Running this creates a temporary file containing lisp commands
# 3. sbcl is executed and calls first "LoadLexiconBuilder" and then
#    the temporary file, and then quits.
#
# if you include -d (for debug) the temporary file is not deleted, so you inspect it

THISDIR=`dirname $0`

usagemsg="Usage: $0 -i <file> -o <dir|file> -v <verb> -d"
debug=0
verb=""

while getopts di:o:v: opt
do
     case $opt in
     i) inname=$OPTARG;;
     d) debug=1;;
     o) outname=$OPTARG;;
     v) verb=$OPTARG;;
     *) echo $usagemsg; exit 1;;
     esac
done

if [ "$inname" == "" -o "$outname" == "" ]; then 
   echo $usagemsg
   exit 1
fi

if [ ! -r $inname ]; then
   echo "can't read $inname";
   exit 1;
fi

indir=`dirname $inname`
infile=`basename $inname`

if [ -d $outname ]; then 
   #if [ -z $verb ]; then
    #  echo $usagemsg
    #  exit 1
   #fi
   outdir=$outname
   outfile=$verb
else
   if [ -f $outname ]; then
      echo "$outname already exists";
      exit 1;
   fi
   outdir=`dirname $outname`
   outfile=`basename $outname`
fi


runfile=run$$;

echo "(defvar *origdir* *default-pathname-defaults*)" > $runfile
echo "(setq *default-pathname-defaults* (merge-pathnames \"$THISDIR/*\"))" >> $runfile
echo "(load \"LoadLexiconBuilder_noun.lsp\")" >> $runfile
echo "(setq *default-pathname-defaults* *origdir*)" >> $runfile
echo "(defparameter *input-directory* \"$indir/\")" >> $runfile
echo "(defparameter *output-directory* \"$outdir/\")" >> $runfile
if [ -z $verb ]; then
    echo "(defparameter *input-file-short-name* \"$infile\")" >> $runfile
    echo "(defparameter *output-file-short-name* \"$outfile\")" >> $runfile
else
   echo "(defparameter *verb-with-files-list* '((\"$verb\" (\"$infile\"))))" >> $runfile
fi
echo "(get-verb-lexs)" >> $runfile
echo "(sb-ext:quit)" >> $runfile

sbcl --disable-debugger --eval "(load \"$runfile\")"

exitStat=$?

if [ $debug -eq 0 ]; then
    rm $runfile
fi

exit $exitStat

