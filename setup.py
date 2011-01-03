from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.event',
      version=version,
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
      url='http://svn.plone.org/svn/plone/plone.event',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'python-dateutil',
          'pytz',
          'zope.component',
          'zope.interface',
          'zope.schema',
          # Problematic imports - those dependencies must go
          'Acquisition',
          'DateTime',
          'Products.CMFPlone',
      ],
      extras_require={'test': [
          #'interlude',
          'DateTime']},
      )
