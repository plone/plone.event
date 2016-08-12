from setuptools import find_packages
from setuptools import setup

version = '1.3.1'

setup(
    name='plone.event',
    version=version,
    description="Event and calendaring related tools not bound to Plone",
    long_description=(open("README.rst").read() + "\n" +
                      open(("CHANGES.rst")).read()),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone calendar calendaring event recurring',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.event',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'python-dateutil',
        'pytz',
        'zope.component',
        'zope.interface',
    ],
    extras_require={
        'test': [
            'DateTime',
            'mock',
            'zope.configuration',
        ],
    },
)
