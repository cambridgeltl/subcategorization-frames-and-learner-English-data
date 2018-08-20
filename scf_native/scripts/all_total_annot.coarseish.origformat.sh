#!/bin/bash

# produces gs in original format

DESTDIR=/usr/groups/dict/panacea/subcat/gold
SCRIPTDIR=/usr/groups/dict/panacea/subcat/scripts
ANNODIR=/usr/groups/dict/panacea/subcat/annotated/domains/userfiles/laura

rm --f $DESTDIR/env.coarse.origformat.v1.0
rm --f $DESTDIR/lab.coarse.origformat.v1.0
touch $DESTDIR/env.coarse.origformat.v1.0
touch $DESTDIR/lab.coarse.origformat.v1.0

# removed from env: accord, change

echo ENV
for verb in use produce include increase say give require rise create take lead seem happen address affect call cause consider continue develop find help make provide reduce show start work
do
  echo $verb >> $DESTDIR/env.coarse.origformat.v1.0
  $SCRIPTDIR/panacea_total_annot.coarseish.origformat.pl 0 0 0 0 $ANNODIR/laura.env.$verb.xml >> $DESTDIR/env.coarse.origformat.v1.0
done

# removed from lab: accord

echo LAB
for verb in work strike dismiss employ organise pay use find include make provide give continue call require consider take allow establish form exist apply set recognise protect concern refuse report entitle
do
  echo $verb >> $DESTDIR/lab.coarse.origformat.v1.0
  $SCRIPTDIR/panacea_total_annot.coarseish.origformat.pl 0 0 0 0 $ANNODIR/laura.lab.$verb.xml >> $DESTDIR/lab.coarse.origformat.v1.0
done
