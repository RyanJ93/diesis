# Diesis

A simple auto-tagging tool for precise music collectors.

This simple tool allows you to automatically tag your audio files by fetching songs information from iTunes APIs and music lyrics from several providers, such as MusixMarch and AZLyrics, directly from your CLI, a GUI version is currently in development.
It supports common audio formats such as _MP3_, _AIFF_, _ALAC (M4A)_, _FLAC_ and _OGG_, Wav support has not been added yet due to a missing featured in a required library (_mutagen_).

## Getting Started

Currently this tool is shipped as a CLI tool, GUI application is currently under development and will be released as soon as possible.

### Requirements

If your are going to install this package using `pip` you don't have to worry about dependencies, however, if you are going to install it manually, all required dependencies are listed in the `requirements.txt` file, here is a quick list:

* _mutagen_: The module used to handle and process the tags from the audio files.
* _beautifulsoup4_: The HTML parser used to scrape lyrics providers (couldn't find good quality APIs, sorry).
* _pydub_: The module used for file conversion, note that it requires `ffmpeg` installed in your system.

### Installation

Installation has been made really simple thanks to the `pip` package manager, you can easily install this tool by typing in your terminal the following command:

```bash
pip install diesis
```

Once installed you can get a list of all the available options by running:

```bash
diesis --help
```

## Contributing, notes and known issues

I made this tool because I broke my HDD containing all my iTunes library. I built my music library very precisely, so I wanted to get it back with all the tags and lyrics associated to the files.
Having just the raw files, I had to do all this annoying work manually, then I created this tool, it made me save months of work without having to waste my life finding those information on the internet like I did before.

As I made it a little quickly, it may be not very stable, one known issue is in file conversion, converting files to Apple Alac (.m4a) will leads to an error, I'm currently trying to figure out the issue.
Anyone who wants to to add features, fix bugs or just kindly help me to understand this issue in file conversion is free to do it and then open a pull request.

Currently my spare time is short so I couldn't manage to write tests so far, I'll so in a near future.

Last note: some information fetched by this application may be protected copyright, such as lyrics, so use this tool for personal use only, please.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.