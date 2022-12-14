#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import os
import re
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('direction', choices=['up', 'down'])
parser.add_argument('server_endpoint', nargs='?', help='hostname:port')
parser.add_argument('server_public_key', nargs='?')
parser.add_argument('--interface-name', '-i', default='wg0')
parser.add_argument('--local-address', '-l', default='192.168.3.1/24')
parser.add_argument('--listen-port', '-p', default='51820')
parser.add_argument('--private-key-path', '--priv-path', default=os.path.expanduser('~/.wg/priv_key'))
parser.add_argument('--allowed-ips', '-a', default='0.0.0.0/0')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

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
if args.direction == 'up':
    p = invoke(f'ip link show {args.interface_name}', check=False)
    if p.returncode:
        invoke(f'sudo ip link add dev {args.interface_name} type wireguard')
        invoke(f'sudo ip address add dev wg0 {args.local_address}')
    invoke('sudo', 'wg',
        'set', args.interface_name,
        'listen-port', args.listen_port,
        'private-key', args.private_key_path,
        'peer', args.server_public_key,
        'allowed-ips', args.allowed_ips,
        'endpoint', args.server_endpoint,
    )
    invoke(f'sudo ip link set up dev {args.interface_name}')
elif args.direction == 'down':
    invoke(f'sudo ip link set down dev {args.interface_name}')
    invoke(f'sudo ip link delete {args.interface_name}')
