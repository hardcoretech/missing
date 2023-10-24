import os
import tempfile

import pytest

from missing import Missing


@pytest.fixture
def temp_git_folder():
    # Create a temp git folder so we could conduct the integration test

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        with open('.gitignore', 'w') as fout:
            fout.write('test_ignore.py')

        os.mkdir('tests')
        os.mkdir(os.path.join('tests', 'ignored'))
        with open(os.path.join('tests', 'ignored', 'test_ignore.py'), 'w'):
            pass

        os.mkdir(os.path.join('tests', 'untracked'))
        with open(os.path.join('tests', 'untracked', 'test_untracked.py'), 'w'):
            pass

        os.mkdir(os.path.join('tests', 'staged'))
        with open(os.path.join('tests', 'staged', 'test_staged.py'), 'w'):
            pass

        os.mkdir('data')
        with open(os.path.join('data', 'user.xml'), 'w'):
            pass

        os.system('git init')
        os.system('git add %s' % os.path.join('tests', 'staged'))
        yield


class TestMissing:
    def test__obey_gitignore(self, temp_git_folder):
        assert 1 == Missing(exclude=[]).run()
        assert not os.path.exists('data/__init__.py')
        assert not os.path.exists('tests/ignored/__init__.py')
        assert os.path.isfile('tests/untracked/__init__.py')
        assert os.path.isfile('tests/staged/__init__.py')
        assert os.path.isfile('tests/__init__.py')
        assert 0 == Missing(exclude=[]).run()

    def test__exclude(self, temp_git_folder):
        assert 0 == Missing(exclude=['tests']).run()
