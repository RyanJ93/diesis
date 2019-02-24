from distutils.core import setup

setup(
    name='Diesis',
    packages=['diesis'],
    version='0.0.1',
    license='MIT',
    description='A simple auto-tagging tool for precise music collectors.',
    author='Enrico Sola',
    author_email='info@enricosola.com',
    url='https://github.com/RyanJ93/diesis',
    keywords=['music', 'tagging', 'id3', 'mp3', 'm4a', 'flac', 'ogg'],
    install_requires=[
        'mutagen',
        'beautifulsoup4',
        'pydub'
    ],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': ['diesis=diesis.main:main']
    }
)
