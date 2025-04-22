#!/usr/bin/env python

import subprocess
import shlex
import argparse
from pathlib import Path



def build_image(board: str, target: str = 'rp2build') -> str:
    cmd = f'./scripts/build_docker_image.py --board {board} --target {target}'
    print(f"Building Docker image for {board} with target {target}...")
    proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"Error building Docker image: {proc.stderr}")
        raise RuntimeError(f"Failed to build Docker image for {board} with target {target}")
    lines = proc.stdout.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('Built image: '):
            image_name = line.split(' ')[-1]
            return image_name
    raise RuntimeError("Failed to find built image name in output.")


def build_firmware(board: str, dest_dir: Path, image_name: str|None = None) -> None:
    if image_name is None:
        image_name = build_image(board)
        print(f'Using Docker image: {image_name}')
    container_build_dir = '/home/app/build'
    mount_args = f'--mount type=bind,source={dest_dir},target={container_build_dir}'
    env_args = f'--env FIRMWARE_DEST={container_build_dir}'
    cmd = f'docker run --rm {mount_args} {env_args} {image_name}'
    print(f"Building firmware for {board}...")
    print(f"Command: {cmd}")
    subprocess.run(shlex.split(cmd), check=True)
    print(f"Firmware for {board} built successfully and saved to {dest_dir}/firmware.")


def main():
    p = argparse.ArgumentParser(description="Build firmware for a specific board.")
    p.add_argument('dest', type=Path, help='The destination directory to save the firmware.')
    p.add_argument('--board', type=str, default='RPI_PICO_W', help='The board to build firmware for.')
    p.add_argument('--image', type=str, default=None, help='The Docker image to use for building firmware.')
    args = p.parse_args()
    args.dest = args.dest.resolve()
    assert args.dest.is_dir(), f"Destination {args.dest} is not a directory."
    for p in args.dest.iterdir():
        if p.is_dir():
            continue
        if p.stem not in ['firmware', 'build_metadata']:
            continue
        print(f"Found file: {p}")
        raise RuntimeError(f"Destination {args.dest} is not empty. Please remove the contents before building.")
    build_firmware(args.board, args.dest, args.image)


if __name__ == '__main__':
    main()
