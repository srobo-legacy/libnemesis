try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'libnemesis',
    'author': 'Sam Phippen',
    'url': 'http://github.com/samphippen/libnemesis',
    'download_url': 'http://github.com/samphippen/libnemesis',
    'author_email': 'samphippen@googlemail.com',
    'version': '0.0.1',
    'install_requires': ['nose', 'python-ldap'],
    'packages': ['libnemesis'],
    'scripts': [],
    'name': 'libnemesis'
}

setup(**config)
