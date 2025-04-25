#!/usr/bin/env python
from __future__ import annotations
import subprocess
import shlex
import argparse


class Version:
    suffix: str|None
    version_tuple: tuple[int, int, int]
    def __init__(self, version: str) -> None:
        self._version = version
        version = version.lstrip('v')
        if '-' in version:
            version, suffix = version.split('-', 1)
            self.suffix = suffix
        else:
            self.suffix = None
        version_parts = [int(p) for p in version.split('.')]
        if len(version_parts) > 3:
            raise ValueError(f"Invalid version format: {version}")
        if len(version_parts) < 3:
            version_parts += [0] * (3 - len(version_parts))
        assert len(version_parts) == 3, f"Invalid version format: {version}"
        self.version_tuple = (version_parts[0], version_parts[1], version_parts[2])

    @property
    def major(self) -> int:
        return self.version_tuple[0]

    @property
    def minor(self) -> int:
        return self.version_tuple[1]

    @property
    def micro(self) -> int:
        return self.version_tuple[2]

    @property
    def is_release(self) -> bool:
        return self.suffix is None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.version_tuple == other.version_tuple

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.version_tuple < other.version_tuple

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.version_tuple <= other.version_tuple

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.version_tuple > other.version_tuple

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.version_tuple >= other.version_tuple

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self) -> str:
        return self._version


def get_latest_tag(repo_url: str) -> str:
    cmd = f'git ls-remote --tags --refs {repo_url}'
    r = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    tags = [
        Version(line.split('refs/tags/')[-1]) for line in r.stdout.splitlines() if line
    ]
    tags = [
        tag for tag in tags if tag.is_release
    ]
    latest = max(tags)
    return str(latest)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--repo', type=str, default='https://github.com/micropython/micropython.git')
    args = p.parse_args()
    latest_tag = get_latest_tag(args.repo)
    print(str(latest_tag))


if __name__ == '__main__':
    main()
