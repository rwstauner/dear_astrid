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

  packages=find_packages(), #['dear_astrid', 'dear_astrid.test'],
  #scripts=['bin/dear_astrid.py'],

  url='http://github.com/rwstauner/dear_astrid/',
  license='MIT',
  description='Migrate tasks from Astrid backup xml',
  long_description=open('README.rst').read(),

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
