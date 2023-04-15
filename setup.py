from setuptools import find_packages
from setuptools import setup


version = "1.4.3.dev0"

setup(
    name="plone.event",
    version=version,
    description="Event and calendaring related tools not bound to Plone",
    long_description=(open("README.rst").read() + "\n" + open("CHANGES.rst").read()),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="Plone calendar calendaring event recurring",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.event",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "python-dateutil",  # >4.0.2
        "pytz",
        "zope.component",
        "zope.interface",
    ],
    extras_require={
        "test": [
            "DateTime",
            "zope.configuration",
        ],
    },
)
