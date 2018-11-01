# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '1.4.0'

setup(
    name='plone.event',
    version=version,
    description="Event and calendaring related tools not bound to Plone",
    long_description=(
        open("README.rst").read() + "\n" + open(("CHANGES.rst")).read()
    ),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords='Plone calendar calendaring event recurring',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.event',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'python-dateutil',  # >4.0.2
        'pytz',
        'zope.component',
        'zope.interface',
    ],
    extras_require={'test': [
        'DateTime',
        'mock',
        'zope.configuration',
    ], },
)
