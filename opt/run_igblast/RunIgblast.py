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


# Parse the yaml file and run IgBLAST accordingly

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys
import os
import os.path
import yaml
import subprocess
from contextlib import contextmanager

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

supported_sets = ['imgt', 'ncbi']
supported_species = {}
# ALthough there are some database files for rhesus_monkey, they are incomplete
supported_species['ncbi'] = ['mouse']
supported_species['imgt'] = ['human', 'mouse', 'rabbit', 'rat']
supported_receptors = ['IG', 'TR']

def main(argv):
    fi = open(os.environ['BBX_MNTDIR'] + '/input/biobox.yaml')
    
    try:
        config = yaml.load(fi)['arguments']
    except:
        print 'Syntax error in biobox.yaml.'
        quit()
            
    seqfile = set_file(config, 'sequences', 'input', True)
    logfile = set_file(config, 'log', 'output', False)
    
    if seqfile is None or logfile is None:
        quit()
        
    if not 'outprefix' in config:
        print 'Error: outprefix not specified in biobox.yaml.'
        quit()

    if not 'germline' in config:
        print 'Error: germline key not present in biobox.yaml'
        quit()
        
    for key in ('set', 'species', 'receptor'):
        if key not in config['germline']:
            print 'Error: %s not specified in germline argument' % key
            quit()
            
    if config['germline']['set'] not in supported_sets:
        print 'Error: germline set %s is not available.' % config['germline']['set'] 
        quit()

    if config['germline']['species'] not in supported_species[config['germline']['set']]:
        print 'Error: germline set %s does not contain species %s.' % (config['germline']['set'], config['germline']['species'])
        quit()

    if config['germline']['receptor'] not in supported_receptors:
        print 'Error: receptor %s is not available.' % config['germline']['receptor']
        quit()
        
    if config['germline']['receptor'] == 'TR':
        if config['germline']['set'] == 'imgt':
            if config['germline']['species'] != 'human' and config['germline']['species'] != 'mouse':
                print 'The IMGT germline set only supports T cell receptor sequences for human and mouse.'
                quit()
        if config['germline']['set'] == 'ncbi':
            print 'The NCBI germline set only supports IG receptor sequences.'
            quit()
            
    germpath = os.environ['BBX_CACHEDIR'] + '/igblast-1.0.0'
    if config['germline']['set'] == 'imgt':
        file_root = config['germline']['set'] + '_' + config['germline']['species'] + '_' + config['germline']['receptor']
    elif config['germline']['set'] == 'ncbi':
        file_root = config['germline']['set'] + '_' + config['germline']['species'] + '_'
        if config['germline']['species'] == 'mouse':
            file_root += 'gl_'
    vfile = germpath + '/' + file_root + 'V'
    dfile = germpath + '/' + file_root + 'D'
    jfile = germpath + '/' + file_root + 'J'
    
    for fn in (vfile, dfile, jfile):
        if not os.path.isfile(fn + '.nhr'):
            print 'Error: germline file %s not found. If you think it should be there, please run the clean command and try again.' % fn
            quit()

    with cd(os.environ['BBX_MNTDIR'] + '/output'):
        igblastdir = os.environ['BBX_OPTDIR'] + '/ncbi-igblast-1.8.0'
        igblastcmd = igblastdir + '/bin/igblastn' 
        cmd = '%s -germline_db_V %s -germline_db_D %s -germline_db_J %s -organism %s -domain_system %s  -query %s -auxiliary_data optional_file/%s_gl.aux -outfmt 3 >%s' % \
              (igblastcmd, vfile, dfile, jfile, config['germline']['species'], 'imgt', seqfile, config['germline']['species'], logfile)
        print 'Running command %s' % cmd
        subprocess.call(cmd, shell=True)
        
        if not os.path.isfile(logfile):
            print 'Error: no output from IgBLAST'
            quit()
            
        blastpluscmd = 'python ' + os.environ['BBX_OPTDIR'] + '/TRIgS/IgBLASTPlus.py'
        cmd = '%s %s %s %s' % (blastpluscmd, seqfile, logfile, config['outprefix'])
        print 'Running command %s' % cmd
        subprocess.call(cmd, shell=True)
    
            
def set_file(config, key, directory, exists):
    if key in config:
        fn = os.environ['BBX_MNTDIR'] + '/' + directory + '/' + config[key]
        if not exists or os.path.isfile(fn):
            return fn
        else:
            print 'Error: %s file %s does not exist.' % (key, fn)
    else:
        print 'Error: argument %s is not present in biobox.yaml.' % key

    return None
        


if __name__ == "__main__":
    main(sys.argv)
