from os import path
from setuptools import setup
import subprocess

repo_url = "https://github.com/emcniece/bchydro"

# Fetch latest tag from Github
cmd = f"git -c 'versionsort.suffix=-' ls-remote --tags --sort='v:refname' {repo_url} | tail -n 1 | cut -d'/' -f3-"
ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
latest_tag = ps.communicate()[0].decode("utf-8").strip()

# Pull PyPi description from README.md
pwd = path.abspath(path.dirname(__file__))
with open(path.join(pwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Pull requirements from local repo
with open(path.join(pwd, "./requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="bchydro",
    packages=["bchydro"],
    version=latest_tag,
    license="MIT",
    description="BCHydro API",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Eric McNiece",
    author_email="emcniece@gmail.com",
    url=repo_url,
    download_url=f"{repo_url}/releases/latest/download/package.tar.gz",
    keywords=["bchydro"],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
