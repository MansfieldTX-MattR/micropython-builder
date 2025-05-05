#!/usr/bin/env python

import subprocess
import shlex
import argparse
from pathlib import Path

HERE = Path(__file__).parent.resolve()
ROOT_DIR = HERE.parent
BUILD_ROOT = ROOT_DIR / 'build'


def build_image(port: str, target: str|None = None) -> str:
    cmd = f'./scripts/build_docker_image.py --port {port} --quiet'
    print(f"Building Docker image for target {target}...")
    proc = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if proc.returncode != 0:
        print(f"Error building Docker image:\n{proc.stderr}\n")
        raise RuntimeError(f"Failed to build Docker image for target {target}")
    image_id = proc.stdout.strip()
    assert len(image_id), "Image ID is empty"
    return image_id


def build_firmware(
    port: str,
    board: str,
    dest_dir: Path,
    image_name: str|None = None,
    **extra_build_meta: str
) -> None:
    if image_name is None:
        image_name = build_image(port=port)
        print(f'Using Docker image: {image_name}')
    container_build_dir = '/home/app/build'
    mount_args = f'--mount type=bind,source={dest_dir},target={container_build_dir}'
    env_args = [
        f'--env FIRMWARE_DEST={container_build_dir}',
        f'--env MPY_BOARD={board}',
    ]
    if extra_build_meta:
        meta_str = ','.join(f'{k}={v}' for k, v in extra_build_meta.items())
        env_args.append(f'--env EXTRA_BUILD_META={meta_str}')
    env_args = ' '.join(env_args)
    cmd = f'docker run --rm {mount_args} {env_args} {image_name}'
    print(f"Building firmware for {board}...")
    print(f"Command: {cmd}")
    subprocess.run(shlex.split(cmd), check=True)
    firmware_file = dest_dir / 'firmware.uf2'
    assert firmware_file.is_file(), f"Firmware file {firmware_file} not found."
    print(f"Firmware for {board} built successfully and saved to {dest_dir}/firmware.")


def main():
    p = argparse.ArgumentParser(description="Build firmware for a specific board.")
    p.add_argument(
        '-d', '--dest', type=Path, default=None,
        help='The destination directory to save the firmware.' \
             ' Defaults to build/<port>/<board>.',
    )
    p.add_argument('--port', type=str, default='rp2', help='The port to build firmware for.')
    p.add_argument('--board', type=str, default='RPI_PICO_W', help='The board to build firmware for.')
    p.add_argument('--image', type=str, default=None, help='The Docker image to use for building firmware.')
    args = p.parse_args()
    if args.dest is None:
        args.dest = BUILD_ROOT / args.port / args.board
    else:
        args.dest = args.dest.resolve()
    args.dest.mkdir(parents=True, exist_ok=True)
    assert args.dest.is_dir(), f"Destination {args.dest} is not a directory."
    existing_files = set[Path]()
    for p in args.dest.iterdir():
        if p.is_dir():
            continue
        if p.stem not in ['firmware', 'build_metadata']:
            continue
        existing_files.add(p)
    if len(existing_files):
        print(f'Destination {args.dest} is not empty:')
        print('\n'.join(f'  - {p.name}' for p in existing_files))
        print('')
        result = input(f'Delete contents? (y/n): ')
        if result.lower() != 'y':
            print('Canelled')
            return
        for p in existing_files:
            p.unlink()

    build_firmware(
        port=args.port, board=args.board,
        dest_dir=args.dest, image_name=args.image
    )


if __name__ == '__main__':
    main()
