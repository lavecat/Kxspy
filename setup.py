from setuptools import setup
import pathlib
import re

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

version = ''

with open('kxspy/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')

setup(
    name='kxspy',
    version=version,
    description='Kxspy is a async python client for KxsClient Network.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lavecat/Kxspy',
    author='lavecat',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='kxsclient, surviv, kxspy, kxs, kxsnetwork',
    packages=["kxspy"],
    install_requires=["aiohttp","numpy"],
    project_urls={
        'Bug Reports': 'https://github.com/lavecat/Kxspy/issues',
        'Source': 'https://github.com/lavecat/Kxspy',
        'Documentation': 'https://kxspy.readthedocs.io/'
    },
)
