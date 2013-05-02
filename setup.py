from setuptools import setup

setup(name='mcat',
    version='1.0',
    description='Run multiple commands and capture their output to 1 stream',
    url='http://github.com/ryazwinski/mcat',
    author='Rick Yazwinski',
    author_email='rick@thinker.ca',
    license='MIT',
    packages=['mcat'],
    zip_safe=False,
    install_requires = [ 'docopt', ],
    entry_points = {
        'console_scripts': ['mcat=mcat:main'],
    }
)
