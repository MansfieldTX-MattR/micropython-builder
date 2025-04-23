#!/usr/bin/env python

import subprocess
import shlex
import argparse


def build_unix_image(target: str, image_name: str):
    cmd = f'docker build -t {image_name} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)


def build_rp2_image(board: str, image_name: str):
    target = 'rp2'
    cmd = f'docker build -t {image_name} --build-arg MPY_BOARD={board} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=str, default='rp2', choices=['rp2', 'unix'])
    p.add_argument('--board', type=str, default='RPI_PICO_W')
    p.add_argument('--target', type=str, default='rp2', choices=['base', 'unix_tests', 'rp2'])
    p.add_argument('--image-name', type=str, required=True)
    args = p.parse_args()
    if args.port == 'unix':
        build_unix_image(args.target, args.image_name)
    elif args.port == 'rp2':
        build_rp2_image(args.board, args.image_name)
    else:
        raise ValueError(f'Unknown port: {args.port}')
    print(f'Built image: {args.image_name}')


if __name__ == '__main__':
    main()
