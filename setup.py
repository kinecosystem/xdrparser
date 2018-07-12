from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='xdrparser',
    version='1.1.0',
    author="Ron Serruya",
    author_email="ron.serruya@kik.com",
    description="Xdr parser for stellar history files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kinecosystem/xdrparser",
    packages=find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Click==6.7',
        'stellar-base==0.1.8.1'
    ],
    entry_points='''
        [console_scripts]
        xdrparser=xdrparser.cli:main
    ''',
    python_requires='>=3.4',
)
