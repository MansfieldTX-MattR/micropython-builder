#!/usr/bin/env python

import subprocess
import shlex
import argparse


def build_unix_image(target: str, image_name: str|None):
    if image_name is None:
        image_name = f'micropython-builder/unix-{target}'.lower()
    cmd = f'docker build -t {image_name} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)
    return image_name


def build_rp2_image(board: str, target: str, image_name: str|None):
    if image_name is None:
        image_name = f'micropython-builder/rp2-{board}-{target}'.lower()
    cmd = f'docker build -t {image_name} --build-arg MPY_BOARD={board} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)
    return image_name


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=str, default='rp2', choices=['rp2', 'unix'])
    p.add_argument('--board', type=str, default='RPI_PICO_W')
    p.add_argument('--target', type=str, default='rp2build', choices=['rp2', 'rp2build', 'rp2test'])
    p.add_argument('--image-name', type=str, default=None)
    args = p.parse_args()
    if args.port == 'unix':
        image_name = build_unix_image(args.target, args.image_name)
    elif args.port == 'rp2':
        image_name = build_rp2_image(args.board, args.target, args.image_name)
    else:
        raise ValueError(f'Unknown port: {args.port}')
    print(f'Built image: {image_name}')


if __name__ == '__main__':
    main()
