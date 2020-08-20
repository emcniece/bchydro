from distutils.core import setup

setup(
    name="bchydro",
    packages=["bchydro"],
    version="0.5",
    license="MIT",
    description="BCHydro API",
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
