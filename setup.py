from setuptools import setup, find_packages

setup(
    name='xdrparser',
    version='1',
    packages=find_packages(),
    include_package_data=True,
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
