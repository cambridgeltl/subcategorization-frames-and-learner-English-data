#!/usr/bin/perl

$thresh = shift;
$file = shift;

open(LEX,$file);

while(<LEX>){
    m/\S+\s+\S+\s+(\S+)/ || die "Bad format";
    if ($1 >= $thresh){print;}
}
