from setuptools import find_packages, setup
from re import search, M

VERSIONFILE = 'meapi/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = search(version_re, version_line, M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(
    name='meapi',
    packages=find_packages(exclude=['tests']),
    version=version,
    description="Unofficial api for 'Me - Caller ID & Spam Blocker' app",
    long_description=(open('README.rst', encoding='utf-8').read()),
    long_description_content_type="text/x-rst",
    author_email='davidlev@telegmail.com',
    project_urls={
        "Documentation": "https://meapi.readthedocs.io",
        "Issue Tracker": "https://github.com/david-lev/meapi/issues",
        "Source Code": "https://github.com/david-lev/meapi",
        "Funding": "https://github.com/sponsors/david-lev"
    },
    author='David Lev',
    license='MIT',
    install_requires=['requests'],
    keywords='me, caller id, spam blocker, meapi',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Telephony',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
