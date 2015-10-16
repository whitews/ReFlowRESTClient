from setuptools import setup

setup(
    name='ReFlowRESTClient',
    version='0.1.3b',
    author='Scott White',
    author_email='scott.white@duke.edu',
    packages=['reflowrestclient'],
    package_data={'': []},
    url='https://github.com/whitews/ReFlowRESTClient',
    license='LICENSE.txt',
    description='REST client for interacting with a ReFlow repository.',
    long_description=open('README.md').read(),
    requires=[
        'requests (>=1.1.0)'
    ]
)
