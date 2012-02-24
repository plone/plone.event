from setuptools import find_packages
from setuptools import setup

import os


setup(
    name='plone.event',
    version='1.0a1',
    description="Event and calendaring related tools not bound to Plone",
    long_description=open("README.txt").read() + "\n" +
           open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://pypi.python.org/pypi?%:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='Plone calendar calendaring event recurring',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/collective/plone.event',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'python-dateutil',
        'pytz',
        'zope.interface',
    ],
    extras_require={
        'test': ['DateTime', 'interlude', 'mock', 'zope.component'],
    },
)
