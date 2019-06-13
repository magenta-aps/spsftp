#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
from setuptools import setup


# Utility function to read the README- and VERSION-files.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


setup(
    name="spsftp",
    version=read("VERSION"),
    author="Jørgen Gårdsted Jørgensen",
    author_email="jgj@magenta-aps.dk",
    description=("library for serviceplatformen sftp"
                 " with trigger- and metadata-files"),
    license="MPL",
    keywords="sftp serviceplatformen",
    url="",
    packages=['spsftp'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MPL License",
    ],
    install_requires=["paramiko", "xmltodict"]
)
