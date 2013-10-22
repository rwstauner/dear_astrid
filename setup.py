# pylint: disable=invalid-name,missing-docstring

from setuptools import setup, find_packages

try:
  import nose.commands
  extra_args = dict(
    cmdclass={'test': nose.commands.nosetests},
  )
except ImportError:
  extra_args = dict()

def lines(f):
  return [l.strip() for l in open(f).readlines()]

def reqs(f):
  # TODO: strip whitespace and parenthesize req versions?
  return lines(f)

tests_require = [
  # Don't require coverage for dist installation.
  r for r in reqs('test-requirements.txt') if "coverage" not in r
]

setup(
  name='dear_astrid',
  version='0.1.0',

  author='Randy Stauner',
  author_email='randy@magnificent-tears.com',

  url='http://github.com/rwstauner/dear_astrid/',
  description='Migrate tasks from Astrid backup xml',
  long_description=open('README.rst').read(),

  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Text Processing',
    'Topic :: Utilities',
  ],
  license='MIT',
  #platforms=

  packages=find_packages(),
  #scripts=['bin/dear_astrid.py'],

  install_requires=reqs('requirements.txt'),

  setup_requires=['nose>=1.0'],

  tests_require=tests_require,

  extras_require={
    'test': tests_require,
  },

  **extra_args
)
