#! /usr/bin/env python3

#===== imports =====#
import copy
import datetime
import os
import re
import subprocess
import sys

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def section(s=None):
    print(blue('-'*40))
    print(timestamp())
    if s: print(s)

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        section()
        print(os.getcwd()+'$', end=' ')
        if any([re.search(r'\s', i) for i in args]):
            print()
            for i in args: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args):
                if i != len(args)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8')
            if out != 'exact': result = result.strip()
        return result

#===== main =====#
assert not os.path.exists(os.path.expanduser('~/.wg/priv_key'))
assert not os.path.exists(os.path.expanduser('~/.wg/pub_key'))
priv_key = invoke('wg genkey', out=True, quiet=True)
os.makedirs(os.path.expanduser('~/.wg'), exist_ok=True)
with open(os.path.expanduser('~/.wg/priv_key'), 'w') as f: f.write(priv_key)
pub_key = invoke('wg pubkey', out=True, input=priv_key.encode(), quiet=True)
with open(os.path.expanduser('~/.wg/pub_key'), 'w') as f: f.write(pub_key)
print(pub_key)
