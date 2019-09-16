import re
from setuptools import setup, find_packages

with open("canopen/__init__.py", "r") as fd:
	version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", fd.read(), re.MULTILINE).group(1)

setup(
	name = "python-canopen",
	version = version,
	packages = find_packages(".", include=["canopen*"]),
	
	install_requires = ["python-can>=3.0.0,<3.2"],
	setup_requires = ["pytest-runner"],
	tests_require = ["pytest", "pytest-timeout", "pytest-cov", "pytest-subtests"],
	
	url = "https://github.com/marcel-kanter/python-canopen"
)
