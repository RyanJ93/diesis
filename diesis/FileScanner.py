from hashlib import md5
from shutil import copyfile
from datetime import datetime
from typing import Set, Optional, List
from pathlib import Path
from diesis import Logger, Song, Config, TagHelper, Converter, Utils
import tempfile
import os


class FileScanner:
    source: str = None
    destination: str = None

    @staticmethod
    def prepare_path(path: Optional[str]) -> Optional[str]:
        """
        Converts the given path into an absolute one.
        :param path: A string containing the path to prepare.
        :type path: Optional[str]
        :return: A string containing the processed path.
        :rtype: Optional[str]
        """
        if path and path[0] == '~':
            path = str(Path.home()) + path[1:]
        return path

    @staticmethod
    def get_allowed_file_types() -> Set[str]:
        """
        Returns all the supported formats according to the classes that are going to be involved in the process.
        :return: A set containing all the file extensions corresponding to the supported formats found.
        :rtype: Set[str]
        """
        if not Config.Config.get_format():
            # If file conversion is disabled, get only the formats supported by the "TagHelper" class.
            return TagHelper.TagHelper.get_supported_formats()
        return TagHelper.TagHelper.get_supported_formats() & Converter.Converter.get_supported_formats()

    def __move(self, song: Song.Song) -> None:
        """
        Renames the file corresponding to the given song using information fetched from iTunes as the new name.
        :param song: An object representing the song to rename.
        :type song: Song.Song
        """
        tmp_path: str = song.get_path()
        length: int = len(self.source) + 1
        original_base_path: str = song.get_original_path()[length:]
        # Use temporary file extension because it contains the converted file extension (in case of conversion).
        extension: str = os.path.splitext(tmp_path)[1].lower()
        filename: str = os.path.splitext(os.path.basename(original_base_path))[0]
        directory: str = ''
        if self.destination and original_base_path.find('/') and not Config.Config.get_flatten():
            # Recursive mode is enabled and original directory hierarchy must be reproduced in destination folder.
            directory = os.path.dirname(original_base_path) + '/'
        if Config.Config.get_rename():
            # New file must be renamed, building the name using information fetched from iTunes.
            filename = song.get_artist() + ' - ' + song.get_title()
        if self.destination:
            base_dir: str = self.destination + '/' + directory
        else:
            base_dir: str = self.source + '/'
        # Remove invalid characters from the user.
        filename = filename.replace('/', '-').replace('\\', '-')
        path: str = base_dir + filename + extension
        # Check if existing file overwrite is allowed or if the new file name doesn't exists.
        if Config.Config.get_overwrite() and os.path.exists(path):
            if directory and not os.path.exists(self.destination + '/' + directory):
                # The file is going to be moved, ensure the folder exists if directory hierarchy must be maintained.
                os.makedirs(self.destination + '/' + directory, 0o777, True)
            # Move temporary created file to its final destination folder.
            os.rename(tmp_path, path)
            return
        i: int = 1
        # Check if new file name exists, in this case, generate new names until a non-existing one is found.
        while os.path.exists(path):
            path = base_dir + filename + ' - ' + str(i) + extension
            i += 1
        if directory and not os.path.exists(self.destination + '/' + directory):
            os.makedirs(self.destination + '/' + directory, 0o777, True)
        # Move the file.
        os.rename(tmp_path, path)

    def __load_eligible_files(self, recursive: bool, context: Optional[str] = None) -> Set[str]:
        """
        Scans the source directory and returns all the supported audio files that will be processed.
        :param recursive: If set to "True" sub-directories will be scanned as well as the source one.
        :type recursive: bool
        :param context: A string containing the directory that must be scanned whenever running in recursive mode.
        :type context: Optional[str]
        :return: A set of strings containing the paths to the files to process.
        :rtype: Set[str]
        """
        file_list: Set[str] = set()
        if context:
            context = context + '/'
        else:
            context = ''
        # Get all the files contained within the given directory.
        files: List[str] = os.listdir(self.source + '/' + context)
        allowed_extensions: Set[str] = FileScanner.get_allowed_file_types()
        # Scan the directory.
        for file in files:
            if recursive and os.path.isdir(self.source + '/' + context + file):
                # If we are running in recursive mode, load the list of all the files contained in this directory.
                internal_list: Set[str] = self.__load_eligible_files(recursive, context + file)
                # Merge the list of all the file loaded from the sub-directory with main one.
                file_list = file_list.union(internal_list)
                continue
            extension: str = os.path.splitext(context + file)[1].lower()[1:]
            compliant: bool = False
            try:
                # Check if the file is supported according to its extension.
                if extension in allowed_extensions:
                    compliant = True
            except ValueError:
                continue
            if compliant:
                # This file appears to be supported, add it to the list.
                file_list.add(context + file)
        return file_list

    def __process_song(self, file: str) -> None:
        """
        Process a given file converting it into a song object.
        :param file: A string containing the path to the song file.
        :type file: str
        """
        Logger.Logger.log('Processing file: ' + file)
        # Generate a random and unique name fo the temporary file copy.
        time: int = datetime.now().microsecond
        extension: str = os.path.splitext(file)[1].lower()
        tmp_path: str = tempfile.gettempdir() + md5(file.encode('utf-8') + str(time).encode('utf-8')).hexdigest()
        tmp_path = tmp_path + extension
        # Create a copy of the original file where all edits will be made.
        copyfile(self.source + '/' + file, tmp_path)
        song: Song.Song = Song.Song(tmp_path, self.source + '/' + file)
        convert_format: Optional[str] = Config.Config.get_format()
        if convert_format:
            # Convert the song into the defined format before start precessing it.
            song.convert(convert_format)
        # Fetch song information from iTunes API.
        song.get_all_info()
        if song.is_found():
            # If information has been found save them.
            song.save()
            self.__move(song)
            if Config.Config.get_remove_original():
                try:
                    os.remove(self.source + '/' + file)
                except OSError:
                    pass
            Logger.Logger.log('Complete processing for file: ' + file + '\n')
            return
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        Logger.Logger.log('Complete processing for file: ' + file + '\n')

    def __init__(self, directory: str = None):
        """
        The class constructor.
        :param directory: A string representing the path to the directory to scan where the songs' files are contained.
        :type directory: str
        """
        self.source = directory

    def set_source(self, source: str) -> None:
        """
        Sets the source directory where the file to process are stored in.
        :param source: A string representing the path to the source directory.
        :type source: str
        :raise ValueError: If an invalid path to the source directory is given.
        """
        if not source:
            raise ValueError('Invalid source directory path.')
        self.source = source

    def get_source(self) -> Optional[str]:
        """
        Returns the source directory where the file to process are stored in.
        :return: A string representing the path to the source directory or None if no source directory has been defined.
        :rtype: Optional[str]
        """
        return self.source

    def set_destination(self, destination: str):
        """
        Sets the directory where processed files will be stored in.
        :param destination: A string containing the path to the destination directory.
        :type destination: str
        """
        self.destination = destination
        return self

    def get_destination(self) -> Optional[str]:
        """
        Returns the path to the directory where processed files will be stored in.
        :return: A string representing the path to the destination directory or None if no directory has been defined.
        :rtype: Optional[str]
        """
        return self.destination

    def scan(self) -> None:
        """
        Processes all the eligible file found within the source directory that has been defined.
        :raise ValueError: If no source directory has been configured.
        """
        # Set source and destination directory, if no custom directories have been previously defined.
        if self.source is None:
            self.source = Config.Config.get_source_directory()
        if self.destination is None:
            self.destination = Config.Config.get_destination_directory()
        if self.source is None:
            raise ValueError('No source directory configured')
        if not os.path.isdir(self.source):
            # If a single file has been given instead of a whole directory, process it directly without looping.
            directory: str = os.path.dirname(self.source)
            filename: str = os.path.basename(self.source)
            # Sets the directory where this file is contained as source directory, then process it.
            self.source = directory
            self.__process_song(filename)
            return
        Logger.Logger.log('Loading files in ' + Utils.Utils.str(self.source))
        # Get the list of the files that are going to be processed.
        recursive: bool = Config.Config.get_recursive()
        file_list: Set[str] = self.__load_eligible_files(recursive)
        if not file_list:
            Logger.Logger.log('No eligible file found, exiting.')
            return
        if self.destination is not None:
            # Check if the destination directory exists, otherwise create it.
            if not os.path.exists(self.destination):
                os.mkdir(self.destination)
        Logger.Logger.log('Ready to process ' + str(len(file_list)) + ' files.')
        for file in file_list:
            self.__process_song(file)
