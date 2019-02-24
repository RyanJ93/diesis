from typing import Set, List, Optional
from diesis import Song, Config
from pydub import AudioSegment


class Converter:
    SUPPORTED_FORMATS: Set[str] = {'m4a', 'mp3', 'alac', 'flac', 'aiff', 'aif', 'ogg'}

    song: Song.Song = None

    @staticmethod
    def get_supported_formats() -> Set[str]:
        """
        Returns the extensions of all the supported file types.
        :return: A set containing the supported file extensions.
        :rtype: Set[str]
        """
        return Converter.SUPPORTED_FORMATS

    def __init__(self, song: Song.Song):
        """
        The class constructor.
        :param song: An instance fo the class "Song" representing the song to convert.
        :type song: Song.Song
        """
        self.set_song(song)

    def set_song(self, song: Song.Song) -> None:
        """
        Sets the song to convert.
        :param song: An instance fo the class "Song" representing the song to convert.
        :type song: Song.Song
        """
        self.song = song

    def get_song(self) -> Song.Song:
        """
        Returns the song to convert.
        :return: An instance fo the class "Song" representing the song to convert.
        :rtype: Song.Song
        """
        return self.song

    def convert(self, conversion_format: str) -> str:
        """
        Convert the file contained within the given song object.
        :param conversion_format: A string containing the format the song must be converted into.
        :type conversion_format: str
        :return: A string containing the path to the converted file.
        :rtype: str
        :raise ValueError: If no song has been defined.
        :raise ValueError: If an invalid or an unsupported format is given.
        """
        # TODO: File conversion into Apple ALAC doesn't work due to a ffmpeg error.
        if self.song is None:
            raise ValueError('No song has been defined.')
        if not conversion_format or conversion_format not in Converter.SUPPORTED_FORMATS:
            raise ValueError('Unsupported format.')
        path: str = self.song.get_path()
        extension: str = self.song.get_extension()
        if extension == conversion_format:
            return path
        arguments: List[str] = []
        new_extension: str = conversion_format
        if conversion_format == 'alac':
            # Patches in CLI arguments based on this command sample:
            # ffmpeg -i input.mp3 -vn -c:a alac output.m4a
            # arguments = ['-vn', '-c:a', 'alac']
            arguments = ['-acodec', 'alac']
            conversion_format = 'aac'
            new_extension = 'm4a'
        elif conversion_format == 'aiff' or conversion_format == 'aif':
            extension = 'aac'
        index: int = path.rfind('.') + 1
        new_path: str = path[:index] + new_extension
        # Generate the object for conversion.
        audio: AudioSegment = AudioSegment.from_file(path, extension)
        # Convert and save the file.
        bitrate: Optional[int] = Config.Config.get_bitrate()
        if bitrate and bitrate > 0:
            audio.export(new_path, format=conversion_format, parameters=arguments, bitrate=bitrate)
        else:
            audio.export(new_path, format=conversion_format, parameters=arguments)
        return new_path
