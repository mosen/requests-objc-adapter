from setuptools import setup, find_packages

setup(
    name="requests-objc-adapter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pyobjc-core',
        'requests'
    ],
)
