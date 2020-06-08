
from distutils.core import setup


setup(
    name='randomnote',
    description='Get familiar with the notes',
    version='0.1',
    packages=['randomnote'],
    install_requires=['pygame'],
    entry_points={
        'console_scripts': ['randomnote=randomnote.main:main']
    }
)
