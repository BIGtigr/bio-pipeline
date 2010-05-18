#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Make LASTZ follow the BLAST convention
"""

import re
import os
import sys
from subprocess import Popen 

non_standard = re.compile("[^ATGCNatgcn]")

def lastz_to_blast(tmp_file, out_fh=sys.stdout):
    fp = file(tmp_file)
    for row in fp:
        atoms = row.strip().split("\t")
        name1, name2, coverage, identity, nmismatch, ngap, \
                start1, end1, start2, end2, score = atoms
        identity = identity.replace("%", "")
        hitlen = coverage.split("/")[1]
        # TODO: evalue formula lookup
        evalue = str(1e-50)
        print >>out_fh,  "\t".join((name1, name2, identity, hitlen, nmismatch, ngap, \
                start1, end1, start2, end2, evalue, score))


def sh(cmd, out_fh=sys.stdout):
    print >>sys.stderr, cmd
    proc = Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    print >>sys.stderr, "job sent to <%d>" % proc.pid
    out, err = proc.communicate()
    print >>sys.stderr, "job <%d> finished" % proc.pid


def get_base_name(st):
    return os.path.basename(st).split(".")[0]


if __name__ == '__main__':
    
    from optparse import OptionParser

    usage = "%prog -i query.fa -d database.fa"
    parser = OptionParser(usage)
    parser.add_option("-i", dest="query", help="query sequence file in FASTA format")
    parser.add_option("-d", dest="target", help="database sequence file in FASTA format")
    parser.add_option("-o", dest="outfile", help="BLAST output [default: stdout]")
    (options, args) = parser.parse_args()

    blast_fields = "query,subject,pctid,hitlen,nmismatch,ngaps,"\
            "qstart,qstop,sstart,sstop,evalue,score"

    lastz_fields = "name2,name1,identity,nmismatch,ngap,"\
            "start2,end2,start1,end1,score"
    
    try:
        afasta_fn = options.query
        bfasta_fn = options.target
        out_fh = file(options.outfile, "w") if options.outfile else sys.stdout
    except:
        sys.exit(parser.print_help())

    if options.query is None or options.target is None:
        sys.exit(parser.print_help())

    tmp_fn = "%s_%s.running.blastz" % (get_base_name(afasta_fn), get_base_name(bfasta_fn))

    lastz_cmd = "lastz --format=general-:%s --transition=2 --ambiguous=iupac %s[multiple] %s --output=%s"
    lastz_cmd = lastz_cmd % (lastz_fields, bfasta_fn, afasta_fn, tmp_fn) 

    sh(lastz_cmd, out_fh=out_fh)
    lastz_to_blast(tmp_fn, out_fh=out_fh)

