from setuptools import setup

setup(
    name='ReFlowRESTClient',
    version='0.0.1',
    author='Scott White',
    author_email='scott.white@duke.edu',
    packages=['reflowrestclient'],
    url='https://github.com/whitews/ReFlowRESTClient',
    license='LICENSE.txt',
    description='REST client for interacting with a ReFlow repository.',
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=1.1.0',
        'grequests>=0.2.0',
        'PIL>=1.1.7',
    ]
)