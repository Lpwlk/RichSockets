from setuptools import setup, find_packages

setup(
    name='richsockets',
    version='0.1.0',
    author='Pawlicki Loic',
    author_email='loic.pawlicki@example.com',
    description='Richsockets is a Python3 CLI package based on socket and rich modules for networking terminal UI rendering.',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)