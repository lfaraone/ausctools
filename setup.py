# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='ausctools',
    version='0.1',
    description='Tools for generating reports for English Wikipedia functionary activity',

    url='https://github.com/lfaraone/ausctools',
    author='Luke Faraone',
    author_email='luke@faraone.cc',

    license='GPL-2+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=[
        "mwclient>=0.7.2",
        "Babel>=2.0",
        "PyYAML",
        "tabulate>=0.6",
    ],

    package_data={
        'examples': ['excuses.yaml.ex'],
    },

    entry_points={
        'console_scripts': [
            'functionary-inactivity-report=inactivity_report:main',
        ],
    },
)
