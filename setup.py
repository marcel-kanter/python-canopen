import re
from setuptools import setup

with open("canopen/__init__.py", "r") as fd:
	version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", fd.read(), re.MULTILINE).group(1)

setup(
	name = "python-canopen",
	version = version,
	packages = ["canopen"],

	setup_requires = ["pytest-runner"],
	tests_require = ["pytest", "pytest-timeout", "pytest-cov"],

	url = "https://github.com/marcel-kanter/python-canopen"
)
