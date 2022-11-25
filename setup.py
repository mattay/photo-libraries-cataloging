"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
  name="catalogue",
  version="0.5.1",
  description="A sample Python project",
  author="Matthew Anderson",  # Optional
  author_email="mattay.anderson@gmail.com",
  keywords="exif",
  package_dir={"": "src"},  # Optional
  packages=find_packages(where="src"),  # Required
  python_requires=">=3.10, <4",
)