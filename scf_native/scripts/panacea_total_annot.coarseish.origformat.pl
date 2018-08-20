#!/usr/bin/perl

$lexpreps = 0;
$lexparticles = 0;
$grouppreps = 0;
$children = 0;

$lexpreps = shift;
$lexparticles = shift;
$grouppreps = shift;
$children = shift;

%scf_counts = ();
$tot = 0;

%map = (
"1" => ":su:xcomp__ADJ:", 
"2" => ":su:xcomp__ADJ:", 
"3" => ":su:", 
"4" => ":su:", 
"5" => ":iobj_PREP-as=>dobj_N:su:", 
"6" => ":ccompthat_VTENSED:dobj_N:su-it:", 
"7" => ":dobj_N:csubjthat_VTENSED:", 
"8" => ":dobj_N:xsubj_VBARE:", 
"9" => ":su-it:xcompto_VBARE:", 
"10" => ":iobj_PREP-for=>dobj_N:su-it:xcompto_VBARE:", 
"11" => ":dobj_N:su-it:xcompto_VBARE:", 
"12" => ":ccompthat_VTENSED:iobj_PREP-to=>dobj_N:su-it:", 
"13" => ":iobj_PREP-to=>dobj_N:su-it:xcompto_VBARE:", 
"14" => ":csubjthat_VTENSED:iobj_PREP-to=>dobj_N:", 
"15" => ":iobj_PREP-for=>dobj_N:su:xcompto_VBARE:", 
"16" => ":ccomp__VTENSED:su:", 
"17" => ":su:xcomp__WHADV=>xcompto_VBARE:", 
"18" => ":su:xcomp__VBARE:", 
"19" => ":su:xcomp__VING:", 
"20" => ":su:xcomp__VING:", 
"21" => ":su:xcomp__VING:", 
"22" => ":su:", 
"23" => ":su:", 
"24" => ":dobj_N:su:", 
"25" => ":dobj_N:su:xcomp__ADJ:", 
"26" => ":dobj_N:su:xcomp__ADJ:", 
"27" => ":dobj_N:su:",  
"28" => ":dobj_N:su:", 
"29" => ":dobj_N:iobj_PREP-as=>dobj_N:su:", 
"30" => ":dobj_N:iobj_PREP-as=>dobj_N:su:", 
"31" => ":dobj_N:iobj_PREP-for=>dobj_N:su:", 
"32" => ":ccomp__VBARE=>su_N:su:", 
"33" => ":ccomp__VBARE=>su_N:su:", 
"34" => ":dobj_N:su:xcomp__VING:", 
"35" => ":dobj_N:su:xcomp__VING:", 
"36" => ":dobj_N:su:xcomp__VING:", 
"37" => ":dobj_N:obj2_N:su:", 
"38" => ":dobj_N:obj2_N:su:", 
"39" => ":dobj_N:su:xcomp__PREP=>xcomp__VING:", 
"40" => ":dobj_N:su:xcomp__PREP=>xcomp__VING:", 
"41" => ":dobj_N:su:xcomp__PREP=>xcomp__VING:", 
"42" => ":dobj_N:su:xcomp__PREP=>xcomp__VING:", 
"43" => ":dobj_N:su:xcomp__PREP=>xcomp__VING:", 
"44" => ":dobj_N:iobj_PREP=>dobj_VING:su:", 
"45" => ":pcomp=>xcomp__WHCOMP:dobj_N:su:", 
"46" => ":pcomp=>dobj_WH:dobj_N:su:", 
"47" => ":pcomp=>dobj_WH:dobj_N:su:", 
"48" => ":pcomp=>xcomp__WHCOMP:dobj_N:su:", 
"49" => ":dobj_N:iobj_PREP=>dobj_N:su:", 
"50" => ":dobj_N:iobj_PREP=>dobj_N:su:", 
"51" => ":dobj_N:su:", 
"52" => ":ccompthat_VTENSED:dobj_N:su:",   # really cc[t]
"53" => ":dobj_N:su:xcompto_VBARE:", 
"54" => ":dobj_N:su:xcompto_VBARE:", 
"55" => ":dobj_N:su:xcompto_VBARE:", 
"56" => ":dobj_N:iobj_PREP-to=>dobj_N:su:", 
"57" => ":dobj_N:su:xcompto_VBARE-be:", 
"58" => ":dobj_N:su:ccomp__VEN:", 
"59" => ":ccomp__WHCOMP=>ccomp__VTENSED:dobj_N:su:", 
"60" => ":ccomp__VTENSED:dobj_N:obj2_WH:su:", 
"61" => ":dobj_N:su:xcomp__WHCOMP=>xcompto_VBARE:", 
"62" => ":dobj_N:obj2_WH:su:", 
"63" => ":xcomp__PREP=>xcomp__VING:su:", 
"64" => ":xcomp__PREP=>xcomp__VING:su:", 
"65" => ":ccomp__PREP=>ccomp__VING:su:", 
"66" => ":iobj_PREP=>dobj_N:su:xcompto_VBARE:", 
"67" => ":iobj_PREP=>dobj_N:su:xcompto_VBARE:", 
"68" => ":iobj_PREP=>dobj_N:su:xcompto_VBARE:", 
"69" => ":ccomp__PREP=>ccomp__VING:su:", 
"70" => ":pcomp=>ccomp__WHCOMP:su:", 
"71" => ":ccomp__PREP=>dobj_WH:su:", 
"72" => ":pcomp=>xcomp__WHCOMP:su:", 
"73" => ":iobj_PREP=>dobj_WH:su:", 
"74" => ":ncmodprt:su:", 
"75" => ":ncmodprt:su:xcomp__VING:", 
"76" => ":dobj_N:ncmodprt:su:", 
"77" => ":dobj_N:iobj_PREP=>dobj_N:ncmodprt:su:", 
"78" => ":iobj_PREP=>dobj_N:ncmodprt:su:", 
"79" => ":ccomp__WHCOMP=>ccomp__VTENSED:ncmodprt:su:", 
"80" => ":ccomp__VTENSED:dobj_WH:ncmodprt:su:", 
"81" => ":ncmodprt:su:xcomp__WHCOMP=>xcompto_VBARE:", 
"82" => ":dobj_WH:ncmodprt:su:", 
"83" => ":ccompthat_VTENSED:ncmodprt:su:", 
"84" => ":su:xcomp__VING=>su:", 
"85" => ":iobj_PREP=>dobj_N:su:xcomp__VING=>su:", 
"86" => ":iobj_PREP=>dobj_N:su:xcomp__VING:", 
"87" => ":iobj_PREP=>dobj_N:su:", 
"88" => ":iobj_PREP=>dobj_N:iobj_PREP-for=>dobj_N:su:", 
"89" => ":ccomp__VTENSED:iobj_PREP=>N:su:", 
"90" => ":iobj_PREP=>dobj_N:su:xcomp__WHMOD=>xcompto_VBARE:", 
"91" => ":iobj_PREP=>dobj_N:pcomp=>ccomp__WHCOMP:su:", 
"92" => ":iobj_PREP=>dobj_N:iobj_PREP=>dobj_WH:su:", 
"93" => ":iobj_PREP=>dobj_N:iobj_PREP=>dobj_WH:su:", 
"94" => ":iobj_PREP=>dobj_N:pcomp_PREP=>xcomp__WHCOMP:su:", 
"95" => ":iobj_PREP=>dobj_N:iobj_PREP=>dobj_N:su:", 
"96" => ":iobj_PREP=>dobj_N:su:", 
"97" => ":ccompthat_VTENSED:iobj_PREP=>dobj_N:su:", 
"98" => ":ccompthat_VBARE:iobj_PREP=>dobj_N:su:", 
"99" => ":iobj_PREP=>dobj_N:su:xcompto_VBARE:", 
"100" => ":ccomp__WHCOMP=>ccomp__VTENSED:iobj_PREP=>dobj_N:su:", 
"101" => ":dobj_WH:iobj_PREP=>dobj_N:su:", 
"102" => ":xcomp__WHCOMP=>xcompto_VBARE:iobj_PREP=>dobj_N:su:", 
"103" => ":dobj_WH:iobj_PREP=>dobj_N:su:", 
"104" => ":ccomp__VTENSED:su:", 
"105" => ":ccompthat_VTENSED:xsubj:",   # really cc[t]
"106" => ":ccompthat_VBARE:su:",     # really cc[t]
"107" => ":ccompthat_VTENSED:su-it:",   # really cc[t]
"109" => ":ccompthat_VTENSED:su:", 
"110" => ":su:xcompto_VBARE:", 
"111" => ":su:xcompto_VBARE:", 
"112" => ":su:xcompto_VBARE:", 
"113" => ":ccomp__WHCOMP=>ccomp__VTENSED:su:", 
"114" => ":dobj_WH:su:", 
"115" => ":xcomp__WHCOMP=>xcompto_VBARE:su:", 
"116" => ":dobj_WH:su:", 
"117" => ":dobj_N:ncmodprt:obj2_N:su:", 
"118" => ":dobj_N:iobj_PREP=>dobj_N:su:", 
"121" => ":iobj_PREP=>dobj_N:iobj_PREP=>dobj_N:ncmodprt:su:", 
"122" => ":dobj_N:iobj_PREP=>dobj_N:iobj_PREP=>dobj_N:su:", 
"123" => ":dobj_N:su:", 
"124" => ":dobj_N:obj2_N:su:", 
"125" => ":dobj_N:ncmodprt:obj2_N:su:", 
"126" => ":ncmodprt:su:", 
"128" => ":ccompthat_VTENSED:ncmodprt:su-it:",   # really cc[t]
"129" => ":csubjthat:", 
"130" => ":ccompthat_VTENSED:dobj_N:ncmodprt:su:", 
"131" => ":ccompthat_VTENSED:iobj_PREP=>dobj_N:ncmodprt:su:", 
"132" => ":ccompthat_VTENSED:dobj_N:obj2_N:su:", 
"133" => ":ccompthat_VBARE:dobj_N:su:", 
"134" => ":ccomp__WHCOMP=>ccomp__VTENSED:dobj-it:su:", 
"135" => ":dobj_WH:iobj_PREP=>dobj_N:su-it:", 
"136" => ":dobj_N:ncmodprt:su:", 
"137" => ":ncmodprt:su:xcomp__ADJ:", 
"138" => ":ncmodprt:su:xcompto_VBARE:", 
"139" => ":ncmodprt:su:xcompto_VBARE:", 
"140" => ":ncmodprt:su:xcompto_VING:", 
"142" => ":su:xcomp__VBARE:", 
"143" => ":dobj_N:su:xc-as=>xcomp__J:", 
"145" => ":dobj_N:ncmodprt:su:xcomp__J:", 
"146" => ":dobj_N:ncmodprt:su:xcomp__J:", 
"147" => ":dobj_N:su:xc-as=>xcomp__J:", 
"148" => ":dobj_N:ncmodprt:su:xc-as=>xcomp__J:", 
"149" => ":dobj_N:ncmodprt:su:xcompto-be=>xcomp__J:", 
"150" => ":dobj_N:ncmodprt:su:xcompto_VBARE:", 
"151" => ":iobj_PREP=>dobj_N:ncmodprt:su:xcompto_VBARE:", 
"152" => ":dobj_N:ncmodprt:su:xcomp__PREP=>xcomp__VING:", 
"153" => ":ccomp__PREP=>ccomp__VBARE:su:", 
"154" => ":xsubjto:", 
"155" => ":dobj:ncmodprt:su:", 
"156" => ":dobj_N:su:xcomp__WHMOD=>xcomp__VTENSED:", 
"157" => ":dobj_N:pcomp-for=>xcompto_VBARE:su:", 
"158" => ":su-it:ccompthat:",   # really cc[t]
"159" => ":su:pcomp-as=>cc-if:", 
"160" => ":su:ncmodprt:", 
"162" => ":dobj_N:su:xc-as=>xcomp__VEN:", 
"163" => ":dobj_N:su:xc-as=>xcomp__VING:", 
"164" => ":su-it:", 
"165" => ":dobj-it:iobj_PREP=>dobj_N:su:xcompto_VBARE:", 
"166" => ":ccompthat_VTENSED:dobj-it:su:",   # really cc[t]
"167" => ":dobj_N:obj2_N:pcomp=>xcompto_VBARE:su-it:", 
"168" => ":dobj_N:obj2_N:su:xcompto_VBARE:", 
"169" => ":ccomp__VTENSED:iobj_PREP=>dobj_N:su:", 
"170" => ":dobj_N:iobj_PREP:su:xcomp__PREP=>xcomp__VING:", 
"171" => ":dobj_N:xsubj_VING:", 
"172" => ":xcomp__VING:xsubj_VING:", 
"173" => ":dobj_N:ncmodprt:su:", 
"174" => ":dobj_N:iobj_PREP-for=>dobj_N:su-it:xcompto_VBARE:", 
"175" => ":dobj_N:su:xcompto_VBARE:", 
"176" => ":iobj_PREP-for=>dobj_N:su-it:xcomp__ADJ:xcompto_VBARE:", 
"177" => ":ccompthat_VTENSED:su-it:xcomp__ADJ:", 
"178" => ":su-it:xcomp__ADJ:xcompto_VBARE:", 
"179" => ":iobj_PREP=>dobj_N:xcompto_VBARE:xsubj_VING:", 
"180" => ":iobj_PREP:su-it:",
"181" => ":su-it:",
"182" => ":ccompthat_VTENSED:iobj_PREP:su-it:xcomp__ADJ:", 
"183" => ":dobj_N:iobj_PREP=>dobj_N:su-it:", 
"184" => ":ccompthat_VTENSED:dobj-it:su:xcomp__ADJ:", 
"185" => ":su:xcompto_VBARE:", 
);

@dirpreps = ("about", "behind", "beyond", "in", "on", "outside", "throughout", "up", "across", "below", "by", "inside", "onto", "over", "to", "along", "beneath", "down", "into", "out", "past", "toward", "via", "around", "between", "from", "off", "through", "toward");


while(<>){

    @sents = split(/\/>/, $_);
    for $s (@sents){
	if($s =~ m/<sentence/ && $s =~ m/verb=/){
	    $s =~ m/scf="(\d+)"/;
	    $prescf = $1;
	    $s =~ m/n="(\d+)"/;
	    $sentnum = $1;
	    if($prescf){  # 0 means invalid sentence

		# get the coarse-ish frame
		$scf = $map{$prescf};
		if ($scf eq "") {print "WARNING: $prescf had no map\n";}
		
		# get particle(s)
		if($lexparticles){
		    if($s =~ m/particles="([^"]+)"/){
		        $parts = $1;
		        @partslist = split(/\-/, $parts);
		        for $p (sort @partslist){
			    $scf =~ s/:ncmodprt:/:ncmodprt-$p:/ || die "Not enough ncmodprt's at sentence $sentnum\n"; # check for particle format, whether there's ncmodprt, etc
	                }
	            }
		}

		# get preposition(s)
                if($lexpreps){
		    if($s =~ m/prepositions="([^"]+)"/){
    		        $preps = $1;
                        if($preps ne ""){
		            @prepslist = split(/\-/, $preps);
                            if($scf =~ /:io/){
  		                for $p (sort @prepslist){

#				    if($grouppreps){
#					if(grep(/^$p$/, @dirpreps)){
#					    $p = "DIR";
#					}
#					else{
#					    $p = "PREP";
#					}
#				    }

                                    # distribute lexicalized preps among ones unlex by the frame
				    $scf =~ s/:io(=>\w+)?:/:io-$p$1:/ || die "Not enough io's at sentence $sentnum\n"; # check for prep format, whether there's io, etc
                                }
                            
                            }
                            elsif($scf =~ /:xc_PREP/){
  		                for $p (sort @prepslist){
			          $scf =~ s/:xc_PREP/:xc_PREP-$p/ || die "Not enough xc_PREP's at sentence $sentnum\n";
                                }
                            }
                        }
		    }
                }

                # group prepositions, both the ones from the lexicalized annotation and the ones originally 
                # lexicalized in the frame definitions
                if($grouppreps){
                    foreach $dirprep (@dirpreps){
		        $scf =~ s/:io\-$dirprep([:=])/:io\-DIR$1/g;
		        $scf =~ s/:xc_PREP\-$dirprep([:=])/:xc_PREP\-DIR$1/g;
                    }
                    $scf =~ s/:io\-[^:=DIR]+/:io\-PREP/g;
                    $scf =~ s/:xc_PREP\-[^:=DIR]+/:xc_PREP\-PREP/g;
		}

                # if unlexicalized, remove prepositions and lexicalizations already in the frame
                if(!$lexpreps){
		    $scf =~ s/\-[a-z]+([^a-z])/$1/g;
		}

		# if no children, remove => already in the frame
		if(!$children){
		    $scf =~ s/=>[a-zA-z_]+:/:/g;
		}


		$scf =~ s/^://;
		$scf =~ s/:$//;

		$scf_counts{$scf}++;
		$tot++;
	    }
	}
    }
}

# print "TOTAL COUNT $tot\n";
print "\n";
for $scf (sort {$scf_counts{$b} <=> $scf_counts{$a}} keys %scf_counts){
    $relfreq = $scf_counts{$scf}/$tot;
    if($scf_counts{$scf} > 1){    # ignore singletons -- but at the moment it's ignoring LEXICALIZED singletons
	printf("%s     %.4f\n", $scf, $relfreq);
    }
}
print "\n";




