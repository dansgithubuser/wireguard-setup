#! /usr/bin/env python3

#===== imports =====#
import copy
import datetime
import os
import re
import subprocess
import sys

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
tf = timestamp_file()
private_key_path = f'private-key-{tf}'
public_key_path = f'public-key-{tf}'

# generate private key
invoke(f'touch {private_key_path}')
invoke(f'chmod 600 {private_key_path}')
with open(private_key_path, 'a') as f:
    invoke('wg genkey', stdout=f)

# generate public key
invoke(f'touch {public_key_path}')
invoke(f'chmod 600 {public_key_path}')
with open(private_key_path) as private_key_file:
    with open(public_key_path, 'a') as public_key_file:
        invoke('wg pubkey', stdin=private_key_file, stdout=public_key_file)

# write config
invoke('sudo touch wg0.conf')
section('writing config to ./wg0.conf')
with open(private_key_path) as private_key_file:
    private_key = private_key_file.read()
content = f'''\
[Interface]
Address = 192.168.6.1/24

ListenPort = 11493

PrivateKey = {private_key}

[Peer]
PublicKey = {client_public_key}
AllowedIPs = 192.168.6.2/32
'''
with open('wg0.conf', 'a') as f:
    f.write(content)
invoke('sudo mv wg0.conf /etc/wireguard/wg0.conf')

# enable & start service
invoke('sudo systemctl enable wg-quick@wg0')
invoke('sudo systemctl start wg-quick@wg0')
