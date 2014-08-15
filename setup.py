"""
This is the setup file to install oa_nlp.
"""

from distutils.core import setup
#from setuptools import setup

def long_description():
    with open('README.md', 'r') as readme:
        readme_text = readme.read()
    return(readme_text)

setup(name='oa_nlp',
      version='0.1.0',
      description='Provides tools for PLOS search API and build NLTK corpora.',
      long_description=long_description(),
      author='Bill OConnor',
      author_email='wtoconnor at gmail dot com',
      url='https://github.com/openAccess/gitPLOS',
      package_dir={'': 'src'},
      packages=['oa_nlp',
                'oa_nlp.nltk',
                'oa_nlp.plos_api',
                ],

      scripts=['bin/plossolr'],
      data_files=[('', ['README.md'])],
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Other Audience',
                   'License :: OSI Approved :: Apache License, Version 2.0',
                   'Programming Language :: Python :: 2.7',
                   'Operating System :: OS Independent',
                   'Topic :: Text Processing :: Markup :: XML',
                   'Topic :: Other/Nonlisted Topic'],
      install_requires=['docopt', 'lxml']
      )
