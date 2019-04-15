from typing import Optional, Any, Set
from argparse import ArgumentParser
from diesis import Converter, FileScanner
import json
import os


class Config:
    WATERMARK: str = 'Processed by Diesis'
    USER_AGENT: str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/35.0.1916.47 Safari/537.36 '

    source: Optional[str] = None
    destination: Optional[str] = None
    verbose: bool = False
    remove_original: bool = False
    watermark: bool = True
    rename: bool = False
    overwrite: bool = False
    strict_meta: bool = False
    strict_lyrics: bool = False
    format: Optional[str] = None
    bitrate: Optional[int] = None
    recursive: bool = False
    flatten: bool = False
    log_file: Optional[str] = None

    @staticmethod
    def __validate() -> None:
        """
        Validates configuration parameters loaded before running the application.
        """
        if not Config.source or not os.path.exists(Config.source):
            print('The given source file or directory does not exist, aborting.')
            quit()

    @staticmethod
    def get_watermark_text() -> str:
        """
        Returns the application signature that will be included in the comment tag in all the processed songs.
        :return: A string containing the application signature.
        :rtype: str
        """
        return Config.WATERMARK

    @staticmethod
    def get_user_agent() -> str:
        """
        Returns the user-agent string to use in HTTP requests.
        :return: A string containing the user-agent to use.
        :rtype: str
        """
        return Config.USER_AGENT

    @staticmethod
    def get_source_directory() -> Optional[str]:
        """
        Returns the path to the directory where the songs to process are located.
        :return: A string containing the path to the source directory
        :rtype: Optional[str]
        """
        return Config.source

    @staticmethod
    def get_destination_directory() -> Optional[str]:
        """
        Returns the path to the directory where the processed songs will be saved in.
        :return: A string containing the path to the destination directory, if no path is defined, "None" is returned.
        :rtype: Optional[str]
        """
        return Config.destination

    @staticmethod
    def is_verbose() -> bool:
        """
        Returns if the verbose logging has been turned on.
        :return: If the verbose logging is enabled will be returned "True".
        :rtype: bool
        """
        return Config.verbose

    @staticmethod
    def get_remove_original() -> bool:
        """
        Returns if the original file must be removed once processed.
        :return: If this option has been enabled will be returned "True".
        :rtype: bool
        """
        return Config.remove_original

    @staticmethod
    def get_watermark() -> bool:
        """
        Returns if a comment containing the application name must be included in the processed files.
        :return: If the watermark is going to be injected will be returned "True".
        :rtype: bool
        """
        return Config.watermark

    @staticmethod
    def get_rename() -> bool:
        """
        Returns if the file must be renamed using information that have been fetched from iTunes once processed.
        :return: If this option has been enabled will be returned "True".
        :rtype: bool
        """
        return Config.rename

    @staticmethod
    def get_overwrite() -> bool:
        """
        Returns if already existing files in destination directory can be overwritten by processed ones.
        :return: If older files can be overwritten will be returned "True".
        :rtype: bool
        """
        return Config.overwrite

    @staticmethod
    def get_strict_meta() -> bool:
        """
        Returns if the application can use a shorter version of the search query when looking for song info on iTunes.
        :return: If the short version of the song search query cannot be used will be returned "True".
        :rtype: bool
        """
        return Config.strict_meta

    @staticmethod
    def get_strict_lyrics() -> bool:
        """
        Returns if the application can use a shorter version of the search query when looking for the song lyrics.
        :return: If the short version of the song search query cannot be used will be returned "True".
        :rtype: bool
        """
        return Config.strict_lyrics

    @staticmethod
    def get_bitrate() -> Optional[int]:
        """
        Returns the bitrate to apply whenever converting an audio file into a lossy format.
        :return: An integer number representing the bitrate in kbps, if none has been defined, None will be returned.
        :rtype: Optional[int]
        """
        return Config.bitrate

    @staticmethod
    def get_format() -> Optional[str]:
        """
        Returns the format that the songs must be converted in once processed.
        :return: A string containing the format, if no format has been defined, "None" will be returned instead.
        :rtype: Optional[str]
        """
        return Config.format

    @staticmethod
    def get_recursive() -> bool:
        """
        Returns if songs contained in sub-directories must be processed as well.
        :return: If sub-directories will be processed will be returned "True"
        :rtype: bool
        """
        return Config.recursive

    @staticmethod
    def get_flatten() -> bool:
        """
        Returns if directory hierarchy found in source directory shouldn't be generated when using the recursive mode.
        :return: If source directory structure shouldn't be generated in destination folder will be returned "True".
        :rtype: bool
        """
        return Config.flatten

    @staticmethod
    def get_log_file() -> Optional[str]:
        """
        Returns the path to the file where log messages should be written in.
        :return: A string containing the path to the log file or None if no path has been defined.
        :rtype: Optional[str]
        """
        return Config.log_file

    @staticmethod
    def setup_from_cli() -> None:
        """
        Parses and loads the given CLI arguments.
        """
        parser: ArgumentParser = ArgumentParser(
            description='A simple auto-tagging tool for precise music collectors.'
        )
        # Set up the accepted arguments and options.
        parser.add_argument(
            'source_path',
            metavar='source',
            type=str,
            nargs='?',
            help='the source directory containing the music files to process.'
        )
        parser.add_argument(
            '--source',
            type=str,
            help='the source directory containing the music files to process.'
        )
        parser.add_argument(
            '--dest',
            nargs='?',
            type=str,
            help='the directory where the processed file must be stored in.'
        )
        parser.add_argument(
            '--format',
            nargs='?',
            type=str,
            help='the format that the songs files must be converted into once processed.'
        )
        parser.add_argument(
            '--bitrate',
            nargs='?',
            type=int,
            help='the bitrate to apply to converted files as kbps integer value.'
        )
        parser.add_argument(
            '--config',
            nargs='?',
            type=str,
            help='the path to a JSON configuration file where settings should be loaded from.'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='enable verbose logging for both normal messages and errors.'
        )
        parser.add_argument(
            '--remove_original',
            action='store_true',
            help='using this option, source files, once processed, are removed from source directory.'
        )
        parser.add_argument(
            '--nowatermark',
            action='store_true',
            help='prevents the application from adding a watermark comment within the processed files meta tags.'
        )
        parser.add_argument(
            '--rename',
            action='store_true',
            help='tells to the application to rename processed files according to information obtained from iTunes API.'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='allows the application to replace files having the same name in destination directory.'
        )
        parser.add_argument(
            '--strict_meta',
            action='store_true',
            help='prevent the application to use a simpler version of the search query to retrieve song information.'
        )
        parser.add_argument(
            '--strict_lyrics',
            action='store_true',
            help='prevent the application to use a simpler version of the search query to retrieve song lyrics.'
        )
        parser.add_argument(
            '--recursive',
            action='store_true',
            help='allows the application to load audio files in subdirectories as well as the given source directory.'
        )
        parser.add_argument(
            '--flatten',
            action='store_true',
            help='using this option, folder hierarchy found in source will not be reproduced in destination directory.'
        )
        parser.add_argument(
            '--log_file',
            nargs='?',
            type=str,
            help='the path to the log file where log messages should be written in.'
        )
        # GET the CLI arguments based on the registered values.
        args = parser.parse_args()
        if args.config:
            Config.load_from_json(args.config)
        # Set up the configuration class.
        source: Optional[str] = args.source
        if not source and args.source_path:
            source = args.source_path
        if source:
            Config.source = FileScanner.FileScanner.prepare_path(source)
        if args.dest:
            Config.destination = FileScanner.FileScanner.prepare_path(args.dest)
        if args.verbose is True:
            Config.verbose = True
        if args.remove_original is True:
            Config.remove_original = True
        if args.nowatermark is True:
            Config.watermark = False
        if args.rename is True:
            Config.rename = True
        if args.overwrite is True:
            Config.overwrite = True
        if args.strict_meta is True:
            Config.strict_meta = True
        if args.strict_lyrics is True:
            Config.strict_lyrics = True
        if args.recursive is True:
            Config.recursive = True
        if args.flatten is True:
            Config.flatten = True
        if args.format and args.format in Converter.Converter.get_supported_formats():
            # Check if the given format is supported by the conversion class.
            Config.format = args.format
        if args.bitrate and args.bitrate > 0:
            Config.bitrate = args.bitrate
        if args.log_file:
            Config.log_file = args.log_file
        # Validate all the loaded parameters before starting.
        Config.__validate()

    @staticmethod
    def load_from_json(path: str) -> None:
        """
        Loads the values of the properties of this class from a given JSON file.
        :param path: A string containing the path to the configuration file.
        :type path: str
        """
        if not path:
            raise ValueError('Invalid file path')
        # Open the given configuration file.
        with open(path, 'rb') as conf:
            contents: str = str(conf.read())
            # Parse its contents as JSON.
            data: Any = json.loads(contents)
            if 'source' in data and type(data['source']) is str and data['source']:
                Config.source = FileScanner.FileScanner.prepare_path(data['source'])
            if 'destination' in data and type(data['destination']) is str and data['destination']:
                Config.destination = FileScanner.FileScanner.prepare_path(data['destination'])
            if 'dest' in data and type(data['dest']) is str:
                Config.destination = data['dest']
            if 'verbose' in data and data['verbose'] is True:
                Config.verbose = True
            if 'remove_original' in data and data['remove_original'] is True:
                Config.remove_original = True
            if 'watermark' in data and data['watermark'] is False:
                Config.watermark = False
            if 'rename' in data and data['rename'] is True:
                Config.rename = True
            if 'overwrite' in data and data['overwrite'] is True:
                Config.overwrite = True
            if 'strict_meta' in data and data['strict_meta'] is True:
                Config.strict_meta = True
            if 'strict_lyrics' in data and data['strict_lyrics'] is True:
                Config.strict_lyrics = True
            formats: Set[str] = Converter.Converter.get_supported_formats()
            # Check if the given conversion format is supported.
            if 'format' in data and type(data['format']) is str and data['format'] and data['format'] in formats:
                Config.format = data['format']
            if 'bitrate' in data and type(data['bitrate']) is int and data['bitrate'] > 0:
                Config.bitrate = data['bitrate']
            if 'recursive' in data and data['recursive'] is True:
                Config.recursive = True
            if 'flatten' in data and data['flatten'] is True:
                Config.flatten = True
