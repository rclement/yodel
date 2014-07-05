from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys
import os
import re
import codecs

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string")

class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name='damn',
    version=find_version('damn', '__init__.py'),
    description='Digital Audio for Music Nerds',
    #long_description=read('README.md'),
    author='Romain Clement',
    author_email='r.clement88@gmail.com',
    url='https://github.com/rclement/damn',
    packages=['damn'],
    tests_require=['tox'],
    cmdclass = {'test': Tox},
    platforms='any',
)
