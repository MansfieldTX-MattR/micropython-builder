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


def build_port_image(
    port: str,
    image_name: str|None,
    target: str|None = None,
) -> None:
    if target is None:
        target = port
    if image_name is not None:
        image_name = f'-t {image_name}'
    else:
        image_name = ''
    cmd = f'docker build {image_name} --target {target} .'
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
    p.add_argument('--target', type=str)
    p.add_argument('--image-name', type=str, default=None)
    args = p.parse_args()
    build_port_image(
        port=args.port, image_name=args.image_name, target=args.target,
    )
    print(f'Built image: {args.image_name}')


if __name__ == '__main__':
    main()
