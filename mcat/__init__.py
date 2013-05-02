#!/usr/bin/env python
"""Image Manager CLI Interface

Usage:
    mcat.py [-t <update>] [-c] [-a color:color:color:...] [-s color:color:color:...] [<cmd>...]

Options:
    -t <update>                 Timeout on checking for updates. Default is 1s.
    -c                          Auto colorize commands
    -a color:color:color:...    When auto colorizing avoid the listed colors
    -s color:color:color:...    Colorize commands as defined. If there are more commands
                                than colors the 1st will be used as default.
"""
import select
import subprocess

try:
    from termcolor import colored, COLORS
except:
    COLORS={'green':1} # ignored anyhow but a dict helps keep things clean
    def colored(text, *args, **kwargs):
        return text

class Mcat():

    _processes = {}
    _colors = {}

    def _split_command(self, cmd):
        import re
        PATTERN = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        return PATTERN.split(cmd)[1::2]

    def __init__(self, commands, color_iterator):
        for c in commands:
            p=subprocess.Popen(self._split_command(c), stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                stdin=None, universal_newlines=True)

            self._processes[p] = c
            self._colors[p.stderr] = self._colors[p.stdout] = color_iterator.next() if color_iterator else None

    def run(self, timeout=1.0):
        while True:
            stderr_list = []
            stdout_list = []
            for p in self._processes.keys():
                if p.poll() is not None:
                    cmd = self._processes[p]
                    print colored('Cmd [%s] exited.' % cmd, 'red')
                    del(self._processes[p])
                    del(self._colors[p.stderr])
                    del(self._colors[p.stdout])
                else:
                    stderr_list.append(p.stderr)
                    stdout_list.append(p.stdout)

            reads = stderr_list + stdout_list
            if len(reads) == 0:
                return

            (read_list, write_list, except_list) = select.select(reads, [], [], timeout)

            for e in read_list:
                line = e.readline().strip()
                if self._colors.has_key(e):
                    color = self._colors[e]
                else:
                    color = 'green'

                if e in stderr_list:
                    out = colored(line, color=color, attrs=['reverse'])
                else:
                    out = colored(line, color=color)

                print out

def color_picker(color_list=None):
    import itertools

    if not color_list:
        for color_list in itertools.repeat(COLORS.keys()):
            for list_elem in color_list:
                yield list_elem
    else:
        for color in color_list:
            yield color

        while True:
            yield color_list[0]

def validate_color_list(color_list):
    unknown_colors = set(color_list)-set(COLORS.keys())
    if len(unknown_colors) > 0:
        raise Exception('Unknown colors: %s' % ', '.join(list(unknown_colors)))

def main():
    import sys
    from docopt import docopt

    arguments = docopt(__doc__)

    try:
        if len(arguments['<cmd>']):
            color_iterator = None
            auto_colorize = arguments.get('-c')
            if auto_colorize:
                avoid = arguments['-a']
                if avoid:
                    avoid_list = ':'.join(avoid).split(':')
                    validate_color_list(avoid_list)
                    for e in avoid_list:
                        if COLORS.has_key(e):
                            del(COLORS[e])
                    if len(COLORS) < 1:
                        print colored('No colors left - exiting.')
                        sys.exit(1)

                color_iterator = color_picker()
            else:
                cmd_line_colors = arguments['-s']
                if len(cmd_line_colors):
                    # may be multiple -s on cli, so join them with a :, then create a list
                    color_list = ':'.join(cmd_line_colors).split(':')
                    validate_color_list(color_list)
                    color_iterator = color_picker(color_list)

            mcat = Mcat(arguments['<cmd>'], color_iterator)

            timeout = arguments.get('-t')
            if timeout is not None:
                timeout = float(timeout)
            else:
                timeout = 1.0

            mcat.run(timeout)

    except Exception as e:
        print 'Fatal problem encountered: ', type(e)
        print '\t', e
        print 'mcat will now exit...\n'
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
