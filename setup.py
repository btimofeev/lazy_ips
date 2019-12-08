from setuptools import setup
from lazy_ips import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='lazy_ips',
    version=__version__,
    description='IPS patcher for Linux. Gtk3 and CLI user interfaces.',
    long_description=long_description,
    author='Boris Timofeev',
    author_email='btimofeev@emunix.org',
    url='https://github.com/btimofeev/lazy_ips',
    license='GNU GPLv3',
    install_requires=['PyGObject'],
    packages=['lazy_ips',
              'lazy_ips.patch'],
    entry_points={"console_scripts": ["lazy-ips-cli=lazy_ips.cli:main"],
                  "gui_scripts": ["lazy-ips=lazy_ips.gtk:main"]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Topic :: Utilities',
    ]
)
