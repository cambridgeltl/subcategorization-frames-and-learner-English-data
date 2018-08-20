#!/usr/bin/perl

# Assuming hard clustering

open(FILE,"verbnet_150_50_200.html");
open(SCFS,"acquired.out");

$frac1 = 0;
$frac2 = 1;

%v_per_c = ();
%cluster_verbs = ();
%verb_clusters = ();
%verb_frames = ();
%cluster_frames = ();
%smoothed_verb_frames = ();

# Read in clusters
while(<FILE>){
    if(m/<Verb label="(.*)">(\w+)<\/Verb>/){
	$c = $1;
	$v = $2;
	$v_per_c{$c}++;
	$cluster_verbs{$c}{$v}++;
	$verb_clusters{$v} = $c;
    }
}

# Read in acquired lexicon
while(<SCFS>){
    m/(\S+)\s+(\S+)\s+(\S+)/ || die;
    $verb_frames{$1}{$2} = $3;
}

# Create averaged distributions for backoff
for $c (keys %cluster_verbs){
    for $v (keys %{$cluster_verbs{$c}}){
	for $s (keys %{$verb_frames{$v}}){
	    $cluster_frames{$c}{$s} += $verb_frames{$v}{$s};
	}
    }
    for $f (keys %{$cluster_frames{$c}}){
	$cluster_frames{$c}{$f} = $cluster_frames{$c}{$f} / $v_per_c{$c};
    }
}

# Smooth by linear interpolation
for $v (keys %verb_frames){
    for $s (keys %{$verb_frames{$v}}){
	$smoothed_verb_frames{$v}{$s} = $frac1 * $verb_frames{$v}{$s};
    }
    for $f (keys %{$cluster_frames{$verb_clusters{$v}}}){
	$smoothed_verb_frames{$v}{$f} += $frac2 * $cluster_frames{$verb_clusters{$v}}{$f};
    }
    for $j (sort {$smoothed_verb_frames{$v}{$b} <=> $smoothed_verb_frames{$v}{$a}} keys %{$smoothed_verb_frames{$v}}){
	print "$v $j $smoothed_verb_frames{$v}{$j}\n";
    }
}

