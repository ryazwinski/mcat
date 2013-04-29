#!/usr/bin/env python
"""Image Manager CLI Interface

Usage:
    mcat.py [-t <update>] [<cmd>...]

Options:
    -t <update>     Timeout on checking for updates. Default is 1s.
"""
import select
import subprocess

class Mcat():

    _processes = []

    def _split_command(self, cmd):
        import re
        PATTERN = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        return PATTERN.split(cmd)[1::2]

    def __init__(self, commands):
        for c in commands:
            p=subprocess.Popen(self._split_command(c), stdout=subprocess.PIPE,stderr=subprocess.STDOUT, stdin=None, universal_newlines=True)
            self._processes.append(p)

    def run(self):
        reads=[x.stdout for x in self._processes]

        while True:
            (read_list, write_list, except_list) = select.select(reads, [], [], 1)
            for e in read_list:
                print e.readline().strip()


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
