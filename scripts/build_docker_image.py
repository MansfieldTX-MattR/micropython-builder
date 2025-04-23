#!/usr/bin/env python
from __future__ import annotations

import subprocess
import shlex
import argparse
from pathlib import Path
import json


HERE = Path(__file__).parent.resolve()
ROOT_DIR = HERE.parent


_port_info = None

def get_port_info() -> dict[str, list[str]]:
    global _port_info
    if _port_info is not None:
        return _port_info
    info_file = ROOT_DIR / 'port_info.json'
    _port_info = json.loads(info_file.read_text())
    return _port_info


def build_unix_image(target: str, image_name: str):
    cmd = f'docker build -t {image_name} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)


def build_rp2_image(board: str, image_name: str):
    target = 'rp2'
    cmd = f'docker build -t {image_name} --build-arg MPY_BOARD={board} --target {target} .'
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)


def validate_board(port: str, board: str|None) -> None:
    port_info = get_port_info()
    if port not in port_info:
        raise ValueError(f'Unknown port: {port}')
    boards = port_info[port]
    if board is not None:
        if len(boards) and board not in boards:
            raise ValueError(f'Unknown board: {board} for port: {port}')
    else:
        if len(boards):
            raise ValueError(f'No board specified for port: {port}, available boards: {boards}')


def main():
    port_info = get_port_info()
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=str, default='rp2', choices=port_info.keys())
    p.add_argument('--board', type=str, default=None)
    p.add_argument('--target', type=str, default='rp2', choices=['base', 'unix_tests', 'rp2'])
    p.add_argument('--image-name', type=str, required=True)
    args = p.parse_args()
    if args.port == 'unix':
        build_unix_image(args.target, args.image_name)
    elif args.port == 'rp2':
        validate_board(args.port, args.board)
        assert args.board is not None
        build_rp2_image(args.board, args.image_name)
    else:
        raise ValueError(f'Unknown port: {args.port}')
    print(f'Built image: {args.image_name}')


if __name__ == '__main__':
    main()
