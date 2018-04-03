from setuptools import setup

setup(name='dsx_decision_optimization_common_utils',
      version='0.1',
      description='Common optimization utilities for use in Python-based optmization projects in IBM DSX',
      url='https://github.ibm.com/DSE/dsx_decision_optimization_common_utils',
      author='Victor Terpstra',
      author_email='vterpstra@us.ibm.com',
      license='MIT',
      packages=['dsx_decision_optimization_common_utils'],
      install_requires=[
          'pandas'
      ],
      zip_safe=False)