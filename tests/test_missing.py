from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from missing import Missing


class File:
    def __init__(self, name: str):
        self.name = name


class Dir:
    def __init__(self, name: str = '.', children: list[Dir | File] | None = None):
        self.name = name
        self.children: list[Dir | File] = children or []


def create_directory_tree(directory: Dir):
    for child in directory.children:
        if isinstance(child, Dir):
            os.mkdir(child.name)
            os.chdir(child.name)
            create_directory_tree(child)
            os.chdir('..')
        else:
            with open(child.name, 'w'):
                pass


@pytest.fixture
def temp_git_folder():
    # Create a temp git folder so that we could conduct the integration test

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        with open('.gitignore', 'w') as fout:
            lines = [
                'ignored.py',
                'ignored_folder/',
                '.hidden_ignored_folder/',
            ]
            fout.write('\n'.join(lines))

        tree = Dir(
            children=[
                Dir(
                    'folder1',
                    [
                        Dir(
                            'folder1_1',
                            [
                                Dir(
                                    'folder1_1_1',
                                    [
                                        File('folder1_1_1.py'),
                                    ],
                                ),
                                Dir(
                                    'folder1_1_2',
                                    [
                                        File('__init__.py'),
                                    ],
                                ),
                            ],
                        ),
                        Dir(
                            'folder1_2',
                            [
                                File('folder1_2.py'),
                            ],
                        ),
                        Dir(
                            'folder_containing_only_ignored_files',
                            [
                                File('ignored.py'),
                            ],
                        ),
                        Dir(
                            'ignored_folder',
                            [
                                File('some_ignored_file.py'),
                            ],
                        ),
                        Dir(
                            '.hidden_ignored_folder',
                            [
                                File('some_ignored_file.py'),
                            ],
                        ),
                        Dir('empty_folder'),
                        File('folder1.py'),
                    ],
                ),
                Dir(
                    'folder2',
                    [
                        Dir(
                            'folder2_1',
                            [
                                File('__init__.py'),
                            ],
                        ),
                        Dir(
                            'folder2_2',
                            [
                                File('folder2_2.py'),
                            ],
                        ),
                        File('folder2.py'),
                        File('__init__.py'),
                    ],
                ),
                Dir(
                    'folder3',
                    [
                        File('other_languages.js'),
                    ],
                ),
                Dir('empty_folder'),
                Dir(
                    'ignored_folder',
                    [
                        File('some_ignored_file.py'),
                    ],
                ),
                Dir(
                    '.hidden_ignored_folder',
                    [
                        File('some_ignored_file.py'),
                    ],
                ),
                File('toplevel.py'),
            ]
        )

        create_directory_tree(tree)

        if shutil.which('tree'):
            subprocess.run(['tree', '-a', '-F', '--dirsfirst'])
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '-A'])
        yield


class TestMissing:
    def test__default(self, temp_git_folder):
        assert 1 == Missing(exclude=[]).run()
        p = Path('.')
        assert not (p / '__init__.py').exists()
        assert not (p / 'folder1' / 'folder1_1' / '__init__.py').exists()
        assert not (p / 'ignored_folder' / '__init__.py').exists()
        assert not (p / '.hidden_ignored_folder' / '__init__.py').exists()
        assert not (p / 'empty_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / 'ignored_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / '.hidden_ignored_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / 'empty_folder' / '__init__.py').exists()
        assert not (p / 'folder3' / '__init__.py').exists()
        assert not (
            p / 'folder1' / 'folder_containing_only_ignored_files' / '__init__.py'
        ).exists()
        assert (p / 'folder1' / '__init__.py').is_file()
        assert (p / 'folder1' / 'folder1_1' / 'folder1_1_1' / '__init__.py').is_file()
        assert (p / 'folder1' / 'folder1_2' / '__init__.py').is_file()
        assert (p / 'folder2' / 'folder2_2' / '__init__.py').is_file()
        assert 0 == Missing(exclude=[]).run()

    def test__exclude(self, temp_git_folder):
        exclude = [
            os.path.join('folder1', 'folder1_1'),
        ]
        assert 1 == Missing(exclude=exclude).run()
        p = Path('.')
        assert not (p / '__init__.py').exists()
        assert not (p / 'folder1' / 'folder1_1' / '__init__.py').exists()
        assert not (p / 'ignored_folder' / '__init__.py').exists()
        assert not (p / '.hidden_ignored_folder' / '__init__.py').exists()
        assert not (p / 'empty_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / 'ignored_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / '.hidden_ignored_folder' / '__init__.py').exists()
        assert not (p / 'folder1' / 'empty_folder' / '__init__.py').exists()
        assert not (p / 'folder3' / '__init__.py').exists()
        assert not (
            p / 'folder1' / 'folder_containing_only_ignored_files' / '__init__.py'
        ).exists()
        assert not (
            p / 'folder1' / 'folder1_1' / 'folder1_1_1' / '__init__.py'
        ).exists()
        assert (p / 'folder1' / '__init__.py').is_file()
        assert (p / 'folder1' / 'folder1_2' / '__init__.py').is_file()
        assert (p / 'folder2' / 'folder2_2' / '__init__.py').is_file()
        assert 0 == Missing(exclude=exclude).run()

    def test__non_str_sequence_exclude_throws_typeerror(self, temp_git_folder):
        with pytest.raises(TypeError):
            Missing(exclude=1)

    def test__non_dir_exclude_throws_typeerror(self, temp_git_folder):
        with pytest.raises(TypeError):
            Missing(exclude=['toplevel.py'])
