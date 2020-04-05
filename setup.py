import os
import sys
from setuptools import setup, find_namespace_packages

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'csiroct', 'server', 'version.py')) as f:
    exec(f.read(), version)

setup(name='csiroct-server',
    version=version['__version__'],
    description='CSIROCT Server',
    long_description=long_description,
    long_description_content_type="text/markdown",      
    url='http://bitbucket.csiro.au',
    author='Darren Thompson',
    author_email='darren.thompson@csiro.au',
    packages=find_namespace_packages(include=['csiroct.*']),
    license='GPL-3.0',    
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],
    )    