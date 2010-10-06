## Copyright (c) 2009, Nathan R. Yergler <nathan@yergler.net>

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the "Software"),
## to deal in the Software without restriction, including without limitation
## the rights to use, copy, modify, merge, publish, distribute, sublicense,
## and/or sell copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.

import os
from setuptools import setup
import pkg_resources

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "rst2slidy",
    version = '0.1', 
    packages = ['rst2slidy'],

    entry_points = {        
        'console_scripts' : [
            'rst2slidy = rst2slidy.cli:main',
            ]
        },
    
    install_requires = ['setuptools',
                        'docutils',
                        ],

    include_package_data = True,
    package_data = {
        'rst2slidy' : ['slidy/*'],
        },
    zip_safe = False,

    author = 'Nathan R. Yergler',
    author_email = 'nathan@yergler.net',
    description = "Tools for creating Slidy presentations with rST and docutils.",
    #long_description = read('README'),
    license = 'BSD',
    url = 'http://gitorious.org/rst2slidy',

    )
