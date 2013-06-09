from setuptools import setup, find_packages

try:
  import nose.commands
  extra_args = dict(
    cmdclass={'test': nose.commands.nosetests},
  )
except ImportError:
  extra_args = dict()

setup(
  name='dear_astrid',
  version='0.1.0',

  author='Randy Stauner',
  author_email='randy@magnificent-tears.com',

  packages=find_packages(), #['dear_astrid', 'dear_astrid.test'],
  #scripts=['bin/dear_astrid.py'],

  url='http://github.com/rwstauner/dear_astrid/',
  #license='LICENSE.txt',
  description='Migrate tasks from Astrid backup xml',
  long_description=open('README.rst').read(),

  install_requires=[
  ],
  setup_requires=['nose>=1.0'],

  **extra_args
)
