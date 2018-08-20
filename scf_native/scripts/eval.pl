#!/usr/bin/perl

# Replaces Yuval's script.

# Doesn't use a raw file atm. Doesn't use frequencies. Type P/R/F only.

$goldfile = shift;
$testfile = shift;

open(GOLD,$goldfile);
open(TEST,$testfile);

%gold_gr_types = ();
%gold_scf_type_freq = ();
%test_scf_type_freq = ();
%gold = ();
%test = ();

%scf_tp = ();
%scf_fn = ();
%scf_fp = ();
%verb_tp = ();
%verb_fp = ();
%verb_fn = ();
$total_tp = 0;
$total_fn = 0;
$total_fp = 0;

$num_gold_verbs = 0;


# Read gold

while(<GOLD>){
    if(m/^\s*(\S+)\s*$/){
	$curverb = $1;
    }
    elsif(m/^\s*([a-zA-Z2\-=>_:]+)\s+[\d\.]+\s*$/){
	$curscf = $1;
	$gold{$curverb}{$curscf}++;
	$gold_scf_type_freq{$curscf}++;
	@curgrtypes = split(":",$curscf);
	for $g (@curgrtypes){$gold_gr_types{$g}++;}
    }
}

# Read test

while(<TEST>){
    m/^\s*(\S+)\s+([a-zA-Z2\-=>_:]+)(_FOO)?/ || die "Unexpected format in test file $testfile line $.\n";
    $curverb = $1;
    $curscf = $2;
    $test{$curverb}{$curscf}++;
    $test_scf_type_freq{$curscf}++;
    @curgrtypes = split(":",$curscf);
    for $g (@curgrtypes){print STDERR "Warning: GR type $g found in test but not gold (verb $curverb)" if !$gold_gr_types{$g};}
}


# Evaluate

$coverage = scalar(keys %gold);
$total_scfs_hypothesized = 0;

for $verb (keys %gold){
    if(!$test{$verb}){print STDERR "Warning: verb $verb in gold standard but not test\n"; $coverage--;}
    else{
	for $goldscf (keys %{$gold{$verb}}){
	    if($test{$verb}{$goldscf}){
		$verb_tp{$verb}{$goldscf}++;
		$test{$verb}{$goldscf} = 0;
		$scf_tp{$goldscf}++;
		$total_tp++;
		$total_scfs_hypothesized++;
	    }
	    else{
		$verb_fn{$verb}{$goldscf}++;
		$scf_fn{$goldscf}++;
		$total_fn++;
	    }
	}
	for $testscf (keys %{$test{$verb}}){
	    if($test{$verb}{$testscf} > 0){  # leftover, otherwise has been set to zero above if tp
		$verb_fp{$verb}{$testscf}++;
		$scf_fp{$testscf}++;
		$total_fp++;
		$total_scfs_hypothesized++;
	    }
	}
    }
}

for $verb (keys %test){
    if(!$gold{$verb}){print STDERR "Warning: verb $verb in test but not gold standard\n";}
    else{
	print "VERB: $verb\n\n";
	print "         CORRECT CLASSES: ";
	for $scf (keys %{$verb_tp{$verb}}){print "$scf   ";}
	print "\n";
	print "  FALSE POSITIVE CLASSES: ";
	for $scf (keys %{$verb_fp{$verb}}){print "$scf   ";}
	print "\n";
	print "         MISSING CLASSES: ";
	for $scf (keys %{$verb_fn{$verb}}){print "$scf   ";}
	print "\n";

	print "\n";

	$perverb_tp = scalar(keys %{$verb_tp{$verb}});
	$perverb_fp = scalar(keys %{$verb_fp{$verb}});
	$perverb_fn = scalar(keys %{$verb_fn{$verb}});

	if($perverb_tp+$perverb_fp > 0){$perverb_p = $perverb_tp/($perverb_tp+$perverb_fp);} else {$perverb_p = 0;}
	if($perverb_tp+$perverb_fn > 0){$perverb_r = $perverb_tp/($perverb_tp+$perverb_fn);} else {$perverb_r = 0;}
	if($perverb_p+$perverb_r > 0){$perverb_f = (2*$perverb_p*$perverb_r)/($perverb_p+$perverb_r);} else {$perverb_f = 0;}

	printf "         P: %6.2f\n", 100*$perverb_p;
	printf "         R: %6.2f\n", 100*$perverb_r;
	printf "         F: %6.2f\n", 100*$perverb_f;
	print "\n\n";
    }
}

@all_scf_types = keys %gold_scf_type_freq;
for $scf (keys %scf_fp){  # include scf types that are only fps, i.e. only in test not gold
    if(!$gold_scf_type_freq{$scf}){
	push(@all_scf_types,$scf);
    }
}

print "BY SCF:\n\n";

for $scf (@all_scf_types){
    if($scf_tp{$scf}){$tp = $scf_tp{$scf};} else {$tp = 0;}
    if($scf_fp{$scf}){$fp = $scf_fp{$scf};} else {$fp = 0;}
    if($scf_fn{$scf}){$fn = $scf_fn{$scf};} else {$fn = 0;}

    if($tp+$fp > 0){$p = $tp/($tp+$fp);} else {$p = 0;}
    if($tp+$fn > 0){$r = $tp/($tp+$fn);} else {$r = 0;}
    if($p+$r > 0){$f = (2*$p*$r)/($p+$r);} else {$f = 0;}

    printf "SCF %s : tp %2d | fp %2d | fn %2d | recall %6.2f%% | precision %6.2f%% | fb %5.2f%%\n",
    $scf, $tp, $fp, $fn, 100*$r, 100*$p, 100*$f

}

print "\n\n";

print "OVERALL:\n\n";

if($total_tp+$total_fp > 0){$total_p = $total_tp/($total_tp+$total_fp);} else {$total_p = 0;}
if($total_tp+$total_fn > 0){$total_r = $total_tp/($total_tp+$total_fn);} else {$total_r = 0;}
if($total_p+$total_r > 0){$total_f = (2*$total_p*$total_r)/($total_p+$total_r);} else {$total_f = 0;}

printf "P: %6.2f\n", 100*$total_p;
printf "R: %6.2f\n", 100*$total_r;
printf "F: %6.2f\n", 100*$total_f;

print "\n";

print "Coverage: $coverage of " . scalar(keys %gold) . " verbs in gold standard\n\n";

printf "Average SCFs hypothesized per verb: %.1f\n", $total_scfs_hypothesized/$coverage;

print "\n";

