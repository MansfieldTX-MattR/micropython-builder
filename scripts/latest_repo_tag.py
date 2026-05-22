#!/usr/bin/env python
from __future__ import annotations
"""Helpers for reading and formatting version tags from a remote git repository."""
import subprocess
import shlex
import argparse


class Version:
    """Comparable semantic version wrapper parsed from git tag strings."""
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

    @property
    def semver(self) -> str:
        """Return the normalized version as major.minor.patch."""
        return f'{self.major}.{self.minor}.{self.micro}'

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
    """Return the newest release tag for the given repository URL."""
    tags = get_release_tags(repo_url)
    if not tags:
        raise RuntimeError(f'No release tags found for repository: {repo_url}')
    return str(tags[0])


def get_remote_tags_output(repo_url: str) -> str:
    """Run git ls-remote and return raw tag lines for a repository."""
    cmd = f'git ls-remote --tags --refs {repo_url}'
    r = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=True)
    return r.stdout


def parse_release_tags(ls_remote_output: str) -> list[Version]:
    """Parse raw ls-remote output, keep release tags only, and sort descending."""
    tags = [
        Version(line.split('refs/tags/')[-1])
        for line in ls_remote_output.splitlines()
        if line and 'refs/tags/' in line
    ]
    tags = [tag for tag in tags if tag.is_release]
    return sorted(tags, reverse=True)


def get_release_tags(repo_url: str, limit: int | None = None) -> list[Version]:
    """Fetch and parse release tags from a repo, optionally limited in count."""
    tags = parse_release_tags(get_remote_tags_output(repo_url))
    if limit is not None:
        tags = tags[:limit]
    return tags


def main():
    """CLI entry point for printing latest or enumerated release tags."""
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--repo', type=str, default='https://github.com/micropython/micropython.git')
    p.add_argument(
        '--list-release-tags',
        action='store_true',
        help='List release tags in descending order (latest first), one per line.',
    )
    p.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of tags returned by --list-release-tags.',
    )
    p.add_argument(
        '--semver',
        action='store_true',
        help='When listing tags, print in major.minor.patch format without a leading v.',
    )
    args = p.parse_args()
    if args.list_release_tags:
        tags = get_release_tags(args.repo, limit=args.limit)
        for tag in tags:
            if args.semver:
                print(tag.semver)
            else:
                print(str(tag))
        return
    latest_tag = get_latest_tag(args.repo)
    print(str(latest_tag))


if __name__ == '__main__':
    main()
