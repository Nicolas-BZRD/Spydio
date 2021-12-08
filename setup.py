from setuptools import setup, find_packages
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Spydio",
    version="0.0.4",
    description="Beta version of Spydio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nicolas-BZRD/spydio",
    author="Nicolas Boizard",
    author_email="nicolas.bzrd@gmail.com",
    license="CC BY-NC-ND 4.0 - Creative Commons",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Other Audience",
        "License :: Free for non-commercial use",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["spydio"],
    package_data={'spydio': ['HRIR/*.sofa']},
    include_package_data=True,
    install_requires=["numpy", "scipy", "SOFASonix"]
)