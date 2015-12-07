#!/usr/bin/env python
import os
import cfg
import sys
import stat

def write_script(d, stage, weightstring=None):
  if not os.path.exists(os.path.join(d.tmpdir,'decoder')):
    if stage not in set(['nbest','forest']):
        raise Exception
    logdir = os.path.join(d.outdir,'logs')
    ruledir = d.config['rules']
    cfg.execute(d,'mkdir -p %s' % logdir)
    cfg.execute(d,'ln -fs %s %s' % (os.path.join(d.config['cprep'],'corpus'), d.tmpdir))
    decodefile = os.path.join(d.tmpdir,'decoder')
    decodescript = open(decodefile,'w')
    infos = []
    print >> decodescript, '#!/usr/bin/env bash'
    print >> decodescript, 'HOST=`hostname`'
    print >> decodescript, 'LOG=%s/decode-log.$HOST-$$.log' % logdir
    print >> decodescript, 'cd %s' % d.tmpdir
    print >> decodescript, 'set -e'
    print >> decodescript, 'set -o pipefail'
    #print >> decodescript, 'ulimit -c unlimited'
    if stage == 'nbest':
        print >> decodescript, 'read inst; rtvl=$?'
        print >> decodescript, '( while [ $rtvl == 0 ]; do cat $inst; read inst; rtvl=$?; done ) | \\'
    print >> decodescript, d.config['decoder']['exec'], "%s/xsearchdb" % ruledir , '--multi-thread \\'
    if 'weights' in d.config:
        print >> decodescript, '  -w %s \\' % os.path.abspath(d.config['weights'])
    
    for k,v in d.config['decoder']['options'].iteritems():
        print >> decodescript,'  --%s %s \\' % (k,v)
    for step in cfg.steps(d):
        if step.stage == 'decode':
            print >> decodescript, '  %s \\' % step.options
            if step.info != '':
                infos.append(step.info)
    if len(infos) > 0:
        print >> decodescript, '  -u %s \\' % ','.join(infos)

    if stage == 'nbest':
        print >> decodescript, '  --output-format nbest \\'
    elif stage == 'forest':
        print >> decodescript, '  --output-format forest \\'
    if stage == 'nbest':
        print >> decodescript, '  2> >(gzip > $LOG.gz) \\'
        print >> decodescript, "|  perl -e '$| = 1; while (<>) { if (~/^.* sent=([^ ]*) .*$/){ print \"$1\\t$_\";} }'"
    elif stage == 'forest':
        print >> decodescript, " 2> >(gzip > $LOG.gz) | sed -u -e 's/@UNKNOWN@//g' " 
    decodescript.close()
    os.chmod(decodefile, stat.S_IRWXU | os.stat(decodefile)[stat.ST_MODE])
    return decodefile