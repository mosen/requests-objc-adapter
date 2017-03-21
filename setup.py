from setuptools import setup, find_packages

install_requires = [
    'pyobjc-core',
    'pyobjc-framework-Cocoa',
    'requests'
]

tests_require = [
    'pytest'
]

setup(
    name="requests-objc-adapter",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
)
