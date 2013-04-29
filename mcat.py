#!/usr/bin/env python
"""Image Manager CLI Interface

Usage:
    mcat.py [-t <update>] [<cmd>...]

Options:
    -t <update>     Timeout on checking for updates. Default is 1s.
"""
import select
import subprocess

try:
    from termcolor import colored
except:
    def colored(text, *args, **kwargs):
        return text

class Mcat():

    _processes = []

    def _split_command(self, cmd):
        import re
        PATTERN = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        return PATTERN.split(cmd)[1::2]

    def __init__(self, commands):
        for c in commands:
            p=subprocess.Popen(self._split_command(c), stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                stdin=None, universal_newlines=True)

            self._processes.append([c, p])

    def run(self):
        while True:
            stderr_list = []
            stdout_list = []
            for [cmd, p] in self._processes:
                if p.poll() == 0:
                    print colored('Cmd [%s] exited.' % cmd, 'red')
                    self._processes.remove([cmd,p])
                else:
                    stderr_list.append(p.stderr)
                    stdout_list.append(p.stdout)

            reads=stderr_list + stdout_list
            if len(reads) == 0:
                return

            (read_list, write_list, except_list) = select.select(reads, [], [], 1)

            for e in read_list:
                line=e.readline().strip()
                if e in stderr_list:
                    out=colored(line, attrs=['reverse'])
                else:
                    out=line
                print out


if __name__ == '__main__':
    import sys
    from docopt import docopt

    arguments = docopt(__doc__)

    try:
        if not arguments.has_key('<cmd>'):
            raise Exception('No <cmd> argument!  Huh!?!')
        
        if len(arguments['<cmd>']):
            mcat = Mcat(arguments['<cmd>'])
            mcat.run()

    except Exception as e:
        print 'Fatal problem encountered: ', type(e)
        print '\t', e
        print 'mcat will now exit...\n'
        raise
    except KeyboardInterrupt:
        pass
