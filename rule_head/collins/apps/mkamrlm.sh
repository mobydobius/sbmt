#!/usr/bin/env bash
SDIR=$(dirname $(readlink -f $0))

IN=$1
OUT=$2
T=$(mktemp -d)
cat $IN | $SDIR/collinsmapper -p ruleinfo > $T/ruleinfo
cat $T/ruleinfo | $SDIR/collinsmapper -p dictionary | cut -f1 | sort -u | $SDIR/mkcollinslm -f $OUT -p dictionary
echo dictionary loaded
$SDIR/mkcollinslm -f $OUT -p amrlm
cat $T/ruleinfo | $SDIR/mkcollinslm -f $OUT -p amrrulemodel 2> $T/events.rulemodel
echo rule model loaded
cat $T/ruleinfo | $SDIR/mkcollinslm -f $OUT -p amrtagmodel 2> $T/events.deptagmodel
echo deptag model loaded
cat $T/ruleinfo | $SDIR/mkcollinslm -f $OUT -p amrwordmodel 2> $T/events.depwordmodel
echo depword model loaded
$SDIR/mkcollinslm -f $OUT -p complete
echo "logs in $T"
