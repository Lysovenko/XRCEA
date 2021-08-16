import setuptools
from os.path import dirname, realpath
from sys import path
try:
    rp = dirname(realpath(__file__))
    path.insert(0, rp)
    from xrcea.core import VERSION
except ImportError:
    VERSION = None

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="XRCEA",
    version=VERSION,
    author="Serhii Lysovenko",
    author_email="Lysovenko@users.noreply.github.com",
    description="X-ray crystallography extensible analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3+",
    url="https://github.com/Lysovenko/XRCEA",
    project_urls={
        "Bug Tracker": "https://github.com/Lysovenko/XRCEA/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 "
        "or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    package_dir={"": "."},
    packages=["xrcea", "xrcea.core", "xrcea.core.vi", "xrcea.core.qt",
              "xrcea.components.bbg",
              "xrcea.components.cryp", "xrcea.components.pddb"],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["xrcea=xrcea.core.application:main"]},
    install_requires=["numpy", "scipy", "PyQt5", "matplotlib"],
    package_data={"xrcea": ["i18n/locale/*/*/*.mo", "doc/*/html/*.*",
                            "doc/*/html/_static/*.*", "components/*.*"]}
)
