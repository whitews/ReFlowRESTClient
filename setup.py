from setuptools import setup

setup(
    name='ReFlowRESTClient',
    version='0.5',
    author='Scott White',
    author_email='scott.white@duke.edu',
    packages=['reflowrestclient'],
    package_data={'': []},
    url='https://github.com/whitews/ReFlowRESTClient',
    license='LICENSE.txt',
    description='REST client for interacting with a ReFlow repository.',
    long_description=open('README.md').read(),
    requires=[
        'requests'
    ]
)
