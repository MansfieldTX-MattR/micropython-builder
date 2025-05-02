#!/usr/bin/env python
from __future__ import annotations
from typing import NewType, Iterator
import subprocess
import shlex
import tempfile
from pathlib import Path
import argparse
import json


PathLike = Path|str
Port = NewType('Port', str)
Board = NewType('Board', str)

HERE = Path(__file__).resolve().parent
ROOT_DIR = HERE.parent
INFO_FILE = ROOT_DIR / 'port_info.json'

MPY_CLONE_URL = 'https://github.com/micropython/micropython.git'
MPY_CLONE_REF = 'master'



class TempDir:
    def __init__(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir.name).resolve()

    def __enter__(self) -> Path:
        return self.temp_dir

    def __exit__(self, *args) -> None:
        self._temp_dir.cleanup()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self) -> str:
        return str(self.temp_dir)


class GitRepo:
    def __init__(self, repo_url: str, branch_ref: str = MPY_CLONE_REF) -> None:
        self.repo_url = repo_url
        self.branch_ref = branch_ref
        self.temp_dir = TempDir()

    @property
    def repo_dir(self) -> Path:
        if self.temp_dir.temp_dir is None:
            raise RuntimeError("Context manager not entered")
        return self.temp_dir.temp_dir

    def clone(self) -> None:
        clone_args = f'--branch {self.branch_ref} --depth 1'
        cmd = f'git clone {clone_args} {self.repo_url} {self.repo_dir}'
        subprocess.run(shlex.split(cmd), check=True)

    def get_path(self, path: PathLike) -> Path:
        if str(path) == '/':
            path = self.repo_dir
        else:
            if not isinstance(path, Path):
                path = Path(path)
            if path.is_absolute():
                if not path.is_relative_to(self.repo_dir):
                    raise ValueError(f"Path {path} is not relative to {self.repo_dir}")
            else:
                path = self.repo_dir / path
        return path

    def ls(self, path: PathLike) -> Iterator[Path]:
        path = self.get_path(path)
        assert path.exists(), f"Path {path} does not exist"
        assert path.is_dir(), f"Path {path} is not a directory"
        d = {p.name: p for p in path.iterdir()}
        for p in sorted(d.keys()):
            yield d[p]

    def ls_dirs(self, path: PathLike) -> Iterator[Path]:
        for item in self.ls(path):
            if item.is_dir():
                yield item

    def __enter__(self) -> Path:
        self.temp_dir.__enter__()
        self.clone()
        return self.repo_dir

    def __exit__(self, *args) -> None:
        self.temp_dir.__exit__(*args)



def iter_ports(repo: GitRepo) -> Iterator[Path]:
    yield from repo.ls_dirs('ports')


def iter_boards(repo: GitRepo, port: Path) -> Iterator[Path]:
    board_dir = port / 'boards'
    if not board_dir.exists():
        return
    yield from repo.ls_dirs(board_dir)


def get_port_info(branch_ref: str = MPY_CLONE_REF) -> dict[Port, list[Board]]:
    port_info: dict[Port, list[Board]] = {}
    repo = GitRepo(MPY_CLONE_URL, branch_ref=branch_ref)
    with repo:
        for port in iter_ports(repo):
            port_name = Port(port.name)
            boards = [Board(b.name) for b in iter_boards(repo, port)]
            port_info[port_name] = boards
    return port_info


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        '--ref',
        type=str,
        default=MPY_CLONE_REF,
        help='Git reference to clone',
    )
    p.add_argument(
        '--latest',
        action='store_true',
        help='Use the latest git tag',
    )
    p.add_argument(
        '-o', '--output',
        type=Path,
        default=INFO_FILE,
        help='Output file',
    )
    args = p.parse_args()
    if args.latest:
        repo_script = HERE / 'latest_repo_tag.py'
        cmd_str = f'{repo_script} --repo {MPY_CLONE_URL}'
        proc = subprocess.run(shlex.split(cmd_str), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to get latest tag: {proc.stderr}")
        args.ref = proc.stdout.strip()
        assert args.ref, "Latest tag is empty"

    args.output = Path(args.output)
    port_info = get_port_info(branch_ref=args.ref)
    args.output.write_text(json.dumps(port_info, indent=2))
    print(f"Port info written to {args.output}")



if __name__ == '__main__':
    main()
