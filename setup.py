import os
from zap import __version__
from setuptools import find_packages
from setuptools import setup


CLASSIFIERS = '''\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Programming Language :: Python
Topic :: Software Development
Operating System :: POSIX :: Linux
'''


setup(
    name='pyappimage',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/srevinsaju/pyappimage',
    license='MIT',
    author='srevinsaju',
    author_email='srevinsaju@sugarlabs.org',
    description='Python Appimage builder',
    project_urls={
        'Bug Tracker': 'https://github.com/srevinsaju/pyappimage/issues',
        'Source Code': 'https://github.com/srevinsaju/pyappimage',
    },
    platforms=['Linux'],
    include_package_data=True,
    package_data={'pyappimage': ['assets/*']},
    install_requires=['PyInstaller', 'click', 'halo', 'pyyaml'],
    dependency_links=[
        "http://github.com/srevinsaju/zap/archive/master.tar.gz"
    ],
    python_requires='>=3.4',
    entry_points={
        'console_scripts': (
            'pyappimage = pyappimage.cli:cli',
        )
    },
    classifiers=[s for s in CLASSIFIERS.split(os.linesep) if s.strip()],
)
