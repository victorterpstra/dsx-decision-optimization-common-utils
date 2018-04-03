from setuptools import setup

setup(name='dsx-decision-optimization-common-utils',
      version='0.1',
      description='Common optimization utilities for use in Python-based optmization projects in IBM DSX',
      url='https://github.ibm.com/DSE/dsx-decision-optimization-common-utils',
      author='Victor Terpstra',
      author_email='vterpstra@us.ibm.com',
      license='MIT',
      packages=['dsx-decision-optimization-common-utils'],
      install_requires=[
          'pandas',
          'glob'
      ],
      zip_safe=False)