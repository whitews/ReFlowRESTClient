from setuptools import setup

setup(
    name='reflowrestclient',
    version='0.0.9',
    author='Scott White',
    author_email='scott.white@duke.edu',
    packages=['reflowrestclient'],
    url='https://github.com/whitews/ReFlowRESTClient',
    license='LICENSE.txt',
    description='REST client for interacting with a ReFlow repository.',
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=1.1.0',
        'Pillow>=2.0.0',
    ]
)