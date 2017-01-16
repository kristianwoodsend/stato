from setuptools import setup


INSTALL_REQUIRES = [
    'Click>=5.0',
    'beautifulsoup4>=4.5.1',
    'fuzzywuzzy>=0.11.1',
    'PuLP>=1.6.1',
    'pyparsing>=1.5.7',
    'python-Levenshtein>=0.12.0',
    'tabulate>=0.7.5'
]

setup(
    name='stato',
    description='dfs optimiser',
    version='0.0.1',
    author='Scott Corbett',

    packages=['stato', 'stato.scrapers'],
    package_data={
        'stato': ['sql/*.sql', 'config/translations.cfg'],
    },
    include_package_data=True,
    package_dir={"": "src"},
    install_requires=INSTALL_REQUIRES,
    entry_points={'console_scripts': ['stato=stato.cli:main']},
)