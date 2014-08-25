from setuptools import setup, find_packages


setup(
    name="fastspring-py",
    packages=find_packages(),
    url="https://github.com/flc/fastspring-py",
    install_requires = ['requests', 'xmltodict'],
)
