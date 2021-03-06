#!/usr/usc/bin/perl

if( scalar(@ARGV)!=6 ){
    die "Usage: intersectMODwVoc.pl grammar.voc grammar.lex ThCnt rules.mod +l|r+ DestDir\n";
}

open(F, $ARGV[0]) or die "Cannot open vocabulary file $ARGV[0]\n";
while($line=<F>){
    chomp($line);
    @line = split " ", $line;
    for($i=0; $i<=$#line; $i++){
	$voc{$line[$i]} = 1;
    }
}
close(F);
$ARGV[0] =~ /^(.*)\/(.*?)$/;
$voc = $2;

open(F, $ARGV[1]) or die "Cannot open lex file $ARGV[1]\n";
while($line=<F>){
    chomp($line);
    @line = split " ", $line;
    $lex{$line[2]} = $line[0];
}
close(F);

$ThCnt = $ARGV[2];
$lex{"+UNK+"} = $ThCnt;

if( $ARGV[3] =~ /^(.*?)\/rules.(.*?).mod.joint=2$/ ){
    $rtype = $2;
}
else{ die "Could not extract type from $ARGV[3]\n"; }
$DestDir = $ARGV[5];
if( $DestDir !~ /\/$/ ){ $DestDir .= "/"; }
$eventsPrefix = "events.";
$out = $DestDir.$eventsPrefix.$rtype.".mod2-1$ARGV[4].$voc";

open(F, $ARGV[3]) or die "Cannot open training MOD file $ARGV[3]\n";
open(O, ">$out") or die "Cannot open output MOD file $out\n";

while($line=<F>){
    chomp($line);
    if( $line =~ /([0-9]+) (.*?) (.*?) (.*?) (.*?) (.*?) \{(.*?)\} (.*?) (.*?) \-\> (.*?) (.*?) (.*?) (.*?)$/ ){
	$cnt = $1; $flag = $2; $P = $3; $H = $4; $t = $5; $w = $6; $C = $7; $V = $8; $T = $9; $M = $10; $mt = $11; $mw = $12; $rest = $13;
	@rest = split " ", $rest;
	if( $rest[0] eq "0" ){ $cc = 0; $ct = 0; $cw = 0; }
	else{ $cc = 1; $ct = $rest[1]; $cw = $rest[2]; }
	if( $cc==0 ){
	    if( $rest[1] eq "0" ){ $punc = 0; $pt = 0; $pw = 0; }
	    else{ $punc = 1; $pt = $rest[2]; $pw = $rest[3]; }
	}
	else{
	    if( $rest[3] eq "0" ){ $punc = 0; $pt = 0; $pw = 0; }
	    else{ $punc = 1; $pt = $rest[4]; $pw = $rest[5]; }
	}
	
	if( $flag ne $ARGV[4] ){ next; }

	if( $M ne "+STOP+"){
	    # mod2-1
	    $w1 = $w;
	    if( $lex{$w} < $ThCnt ){ $w1 = "+UNK+"; }
	    $mw1 = $mw; $ignore = 0;
	    if( $lex{$mw} < $ThCnt ){ $mw1 = "+UNK+"; }
	    $joint = "+mod2-1+ $flag $P {$C} $V $T $H $t $w1 $M $mt $cc $punc -> $mw1";
	     $cond = "+mod2-1+ $flag $P {$C} $V $T $H $t $w1 $M $mt $cc $punc";
	    if( !$voc{$mw} && $lex{$mw} >= $ThCnt ){ $ignore = 1; }
	    if( $w1 eq "+UNK+" || $voc{$w} ){
		record($joint, $cond, $cnt, $ignore);
	    }
	}
    }
    else{ print STDERR "Error in this line: $line\n" and die; }
}
close(F);

foreach $key (keys %jointCnt){
    $ckey = $key;
    $jcnt = $jointCnt{$ckey}[0];
    $key =~ s/ \-\> (.*?)$//;
    $ccnt = $condCnt{$key}[0];
    $ucnt = $condCnt{$key}[1];
    if( $jointCnt{$ckey}[1] ){
	if( !$markedCond{$key} ){
	    print O "$key -> +N/A+ | 0 $ccnt $ucnt\n";
	    $markedCond{$key} = 1;
	}
    }
    else{
	print O "$ckey | $jcnt $ccnt $ucnt\n";
    }
}

sub record{
    my ($joint, $cond, $cnt, $ignore) = @_;

    $newevent = 0;
    if( $jointCnt{$joint} ){
	$jointCnt{$joint}[0] += $cnt;
    }
    else{ 
	$jointCnt{$joint}[0] = $cnt;
	$jointCnt{$joint}[1] = $ignore;
	$newevent = 1;
    }

    $condCnt{$cond}[0] += $cnt;
    if( $newevent ){
	$condCnt{$cond}[1] += 1;
    }
}
