#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

REQUIREMENTS = ['flask',
                'soundfile']

SETUP_REQUIREMENTS = ['pytest-runner', ]

TEST_REQUIREMENTS = ['pytest>=3', ]

setup(
    author="Fred Osterrath",
    author_email='frederic.osterrath@mila.quebec',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="This is the code base for a WEB interface to conduct user"
                "experiments for the Mila DeepGroove project.",
    entry_points={
        'console_scripts': [
            'deepgroove_web_user_experiment='
            'deepgroove_web_user_experiment.cli:main',
        ],
    },
    install_requires=REQUIREMENTS,
    license="BSD license",
    include_package_data=True,
    keywords='deepgroove_web_user_experiment',
    name='deepgroove_web_user_experiment',
    packages=find_packages(include=['deepgroove_web_user_experiment',
                                    'deepgroove_web_user_experiment.*']),
    setup_requires=SETUP_REQUIREMENTS,
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
    url='https://github.com/fosterrath-mila/deepgroove_web_user_experiment',
    version='0.1.0',
    zip_safe=False,
)
