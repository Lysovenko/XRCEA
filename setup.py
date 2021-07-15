import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="XRCEA",
    version="0.0.1",
    author="Serhii Lysovenko",
    author_email="Lysovenko@users.noreply.github.com",
    description="X-ray crystallography extensible analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        "Natural Language :: Ukrainian",
        "Natural Language :: English",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
