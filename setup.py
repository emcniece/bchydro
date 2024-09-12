from os import path
from setuptools import setup

repo_url = "https://github.com/emcniece/bchydro"
pwd = path.abspath(path.dirname(__file__))

# Extract package version
with open(path.join(pwd, "VERSION"), encoding="utf-8") as f:
    version = f.read()

# Pull PyPi description from README.md
with open(path.join(pwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bchydro",
    packages=["bchydro"],
    version=version,
    license="MIT",
    description="BCHydro API",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Eric McNiece",
    author_email="emcniece@gmail.com",
    url=repo_url,
    download_url=f"{repo_url}/releases/latest/download/package.tar.gz",
    keywords=["bchydro"],
    install_requires=[
        "aiohttp<=3.7.3",
        "beautifulsoup4<=4.9.3",
        "tenacity<=6.3.1",
        "ratelimit<=2.2.1",
        "pyppeteer<=1.0.2",
    ],
    extras_require={
        "dev": [
            "pip-tools<=7.4.1",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
