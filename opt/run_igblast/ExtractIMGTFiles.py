# Copyright (c) 2015 William Lees

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Extract gene files for supported species from the IGBLAST gene library 

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import os
import os.path
import shutil
import stat
from contextlib import contextmanager
import argparse
from Bio import SeqIO
import subprocess

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

# from http://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(src, dst, symlinks = False, ignore = None, prefix = ''):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, prefix+item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
        
wanted = {}
wanted['Homo sapiens'] = 'human'
wanted['Mus musculus'] = 'mouse'
wanted['Oryctolagus cuniculus'] = 'rabbit'
wanted['Rattus norvegicus'] = 'rat'


def main(argv):
    germpath = os.environ['BBX_CACHEDIR'] + '/igblast-1.0.0'
    if not os.path.exists(germpath):
        os.makedirs(germpath)
        
    if os.path.exists(germpath + '/complete'):
        print 'Using pre-existing germline files in cache.'
        quit()
    
    print 'Installing germline files in cache %s.' % germpath
        
    with cd(germpath): 
        try:
            subprocess.call("rm *", shell=True)
        except:
            pass
        
        copytree(os.environ['BBX_OPTDIR'] + '/ncbi-igblast-1.8.0/database', germpath, prefix='ncbi_')
        subprocess.call("wget -O imgt_germlines.fasta http://www.imgt.org/download/GENE-DB/IMGTGENEDB-ReferenceSequences.fasta-nt-WithoutGaps-F+ORF+inframeP", shell=True)
        
        recs = list(SeqIO.parse('imgt_germlines.fasta', 'fasta'))
        fastafiles = []
        
        for sp,cn in wanted.iteritems():
            outrecs = {}
            for rec in recs:
                d = rec.description.split('|')
                if len(d) > 4 and sp in d[2] and d[4] in ['V-REGION', 'D-REGION', 'J-REGION']:
                    seg = d[4][0]
                    rec.description = d[1]
                    rec.id = d[1]
                    key = d[1][:2] + seg
                    if key not in outrecs:
                        outrecs[key] = []
                    outrecs[key].append(rec)
            for fn, r in outrecs.iteritems():
                fastafile = 'imgt_' + cn + '_' + fn + '.fasta'
                SeqIO.write(r, fastafile, 'fasta')
                fastafiles.append(fastafile)
        
        igblastpath = os.environ['BBX_OPTDIR'] + '/ncbi-igblast-1.8.0'
        for fn in fastafiles:
            print 'Processing germline file %s' % fn
            cmd = '%s/bin/makeblastdb -parse_seqids -dbtype nucl -in %s -out %s' % (igblastpath, fn, fn.replace('.fasta', ''))
            print cmd
            subprocess.call(cmd, shell=True)        

        print 'Germline file processing complete.'
        subprocess.call('touch complete', shell=True)

if __name__ == "__main__":
    main(sys.argv)
                