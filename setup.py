import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
    'python-twitter',
    'nlpnet',
    'nltk',
    'rdflib',
    'oauthlib',
    'PasteScript',
    'gensim',
    'googlemaps',
    'beaker'
    ]


setup(name='LBSociam',
      version='0.5',
      description='LBSociam',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Nltk",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Eduardo Santos',
      author_email='eduardo@eduardosan.com',
      url='',
      keywords='web semantic',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="lbsociam",
      entry_points="""\
      [paste.paster_command]
        lbtwitter = lbsociam.commands:TwitterCommands
        crime = lbsociam.commands:CrimeCommands
        dictionary = lbsociam.commands:DictionaryCommands
        analytics = lbsociam.commands:AnalyticsCommands
        location = lbsociam.commands:LocationCommands
      """,
      )

