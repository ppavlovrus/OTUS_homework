from setuptools import setup, find_packages

setup(
   name='nginx_log_analyzer',
   version='0.1',
   description='A log analyzer for OTUS course',
   author='Pavel Pavlov',
   author_email='ppavlovrus@gmail.com',
   packages=find_packages(),
   install_requires=['datetime', 'json', 'os', 're', 'collections', 'statistics', 'decimal']
)