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
parser.add_argument('--setup', metavar='peer_names', nargs='*')
parser.add_argument('--show-peer', metavar='peer_name')
parser.add_argument('--rotate-peer', metavar='peer_name')
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

def timestamp_file():
    return '{:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())

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
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.setup != None:
    peer_names = args.setup
    invoke('docker pull linuxserver/wireguard:latest')
    invoke(  # https://github.com/linuxserver/docker-wireguard#docker-cli-click-here-for-more-info
        'docker', 'run', '-d',
        '--name=wireguard',
        '--cap-add=NET_ADMIN',
        '--cap-add=SYS_MODULE',
        '-e', 'PUID=1000',  # corresponds to `id $user` uid
        '-e', 'PGID=1000',  # corresponds to `id $user` gid
        '-p', '51820:51820/udp',
        '-e', 'PEERS='+','.join(peer_names),
        '-v', f'{DIR}/config:/config',
        '--restart=always',
        'linuxserver/wireguard',
    )

if args.show_peer:
    peer_name = args.show_peer
    invoke(f'docker exec wireguard cat /config/peer_{peer_name}/peer_{peer_name}.conf')

if args.rotate_peer:
    peer_name = args.rotate_peer
    invoke(f'docker exec wireguard rm -rf /config/peer_{peer_name}/peer_{peer_name} /config/wg0.conf')
    invoke('docker restart wireguard')
