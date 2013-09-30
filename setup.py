# pylint: disable=invalid-name,missing-docstring

from setuptools import setup, find_packages

try:
  import nose.commands
  extra_args = dict(
    cmdclass={'test': nose.commands.nosetests},
  )
except ImportError:
  extra_args = dict()

# TODO: would this work? (is the file included in the dist?)
#tests_require = [l.strip() for l in open('test-requirements.txt').readlines()]
tests_require = ['mock']

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
    'Programming Language :: Python :: 3',
    'Topic :: Text Processing',
    'Topic :: Utilities',
  ],
  license='MIT',
  #platforms=

  packages=find_packages(),
  #scripts=['bin/dear_astrid.py'],

  install_requires=[
    'pyrtm>=0.4.1',
  ],

  setup_requires=['nose>=1.0'],

  tests_require=tests_require,

  extras_require={
    'test': tests_require,
  },

  **extra_args
)
