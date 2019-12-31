import re
from setuptools import setup, find_packages

with open("canopen/__init__.py", "r") as fd:
	version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", fd.read(), re.MULTILINE).group(1)

with open("readme.rst", "r") as f:
	long_description = f.read()

setup(
	name = "python-canopen",
	url = "https://github.com/marcel-kanter/python-canopen",
	description = "CANopen package for python",
	long_description = long_description,
	version = version,
	packages = find_packages(".", include=["canopen*"]),
	
	install_requires = ["python-can>=3.0.0,<3.2"],
	setup_requires = ["pytest-runner"],
	tests_require = ["pytest", "pytest-timeout", "pytest-cov", "pytest-subtests"],
	
	
	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Intended Audience :: Healthcare Industry",
		"Intended Audience :: Information Technology",
		"Intended Audience :: Manufacturing",
		"Intended Audience :: Science/Research",
		"Intended Audience :: Telecommunications Industry",
		"License :: Other/Proprietary License",
		"Operating System :: MacOS",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
		"Topic :: System :: Networking",
		"Topic :: Software Development",
		"Topic :: Software Development :: Testing",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Utilities"
		]
)
