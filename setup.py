from setuptools import setup, find_packages

setup(
    name='xdrparser',
    version='1',
    py_modules=['cli','parser'],
    install_requires=[
        'Click==6.7',
        'stellar-base==0.1.8.1'
    ],
    entry_points='''
        [console_scripts]
        xdrparser=cli:main
    ''',
    python_requires='>=3.4',
)
