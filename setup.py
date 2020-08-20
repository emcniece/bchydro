from os import path
from distutils.core import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bchydro",
    packages=["bchydro"],
    version="0.6",
    license="MIT",
    description="BCHydro API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Eric McNiece",
    author_email="emcniece@gmail.com",
    url="https://github.com/emcniece/bchydro",
    download_url="https://github.com/emcniece/bchydro/releases/latest/download/package.tar.gz",
    keywords=["bchydro"],
    install_requires=["beautifulsoup4"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
