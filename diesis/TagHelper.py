from typing import Set, Any
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, TCON, USLT, TPOS, TRCK, APIC, COMM, TPE2, WOAF, PictureType, TEXT
from mutagen.flac import FLAC, Picture
from mutagen.aiff import AIFF
from diesis import Song, Config
import mutagen
import base64


class TagHelper:
    SUPPORTED_FORMATS: Set[str] = {'m4a', 'mp3', 'flac', 'aiff', 'aif', 'ogg'}

    song: Song = None

    @staticmethod
    def __str(value: Any) -> str:
        """
        Converts a given value into a string converting "None" values into an empty string instead of a literal "None".
        :param value: The value to convert.
        :type value: Any
        :return: The string representation of the given value.
        :rtype: str
        """
        if value is None:
            return ''
        return str(value)

    def __save_m4a(self) -> None:
        """
        Sets the file tags according to song properties using the format required by M4A files.
        """
        tags: Any = self.song.get_tag_object()
        # Set the tags value according to song properties.
        tags['©nam'] = [TagHelper.__str(self.song.get_title())]
        tags['©ART'] = [TagHelper.__str(self.song.get_artist())]
        tags['aART'] = [TagHelper.__str(self.song.get_album_artist())]
        tags['©alb'] = [TagHelper.__str(self.song.get_album())]
        tags['©day'] = [TagHelper.__str(self.song.get_year())]
        tags['©gen'] = [TagHelper.__str(self.song.get_genre())]
        tags['©wrt'] = [TagHelper.__str(self.song.get_composer())]
        tags['©grp'] = [TagHelper.__str(self.song.get_group())]
        if self.song.get_explicit():
            tags['rtng'] = [1]
        else:
            tags['rtng'] = [2]
        tags['©lyr'] = [TagHelper.__str(self.song.get_lyrics())]
        # TODO: Currently not supported song's properties: track_url, album_url, lyrics_writer
        i: int = self.song.get_disc_number()
        total: int = self.song.get_disc_count()
        if i > 0 and total > 0:
            tags['disk'] = [(
                self.song.get_disc_number(),
                self.song.get_disc_count()
            )]
        i = self.song.get_track_number()
        total = self.song.get_track_count()
        if i > 0 and total > 0:
            tags['trkn'] = [(
                self.song.get_track_number(),
                self.song.get_track_count()
            )]
        # Generate the tag representation of the cover image, if defined.
        if self.song.get_cover_path() is not None:
            with open(self.song.get_cover_path(), 'rb') as cover:
                tags['covr'] = [MP4Cover(cover.read(), imageformat=MP4Cover.FORMAT_JPEG)]
        if Config.Config.get_watermark():
            # Add the application watermark.
            tags['©cmt'] = Config.Config.get_watermark_text()
        # Save the edited tags to the file.
        tags.save()

    def __save_id3(self) -> None:
        """
        Sets the file tags according to song properties using the ID3 format.
        """
        tags: Any = self.song.get_tag_object()
        # Set the tags value according to song properties.
        tags['TIT2'] = TIT2(encoding=3, text=TagHelper.__str(self.song.get_title()))
        tags['TPE1'] = TPE1(encoding=3, text=TagHelper.__str(self.song.get_artist()))
        tags['TPE2'] = TPE2(encoding=3, text=TagHelper.__str(self.song.get_album_artist()))
        tags['TALB'] = TALB(encoding=3, text=TagHelper.__str(self.song.get_album()))
        tags['TYER'] = TYER(encoding=3, text=TagHelper.__str(self.song.get_year()))
        tags['TCON'] = TCON(encoding=3, text=TagHelper.__str(self.song.get_genre()))
        tags['TCOM'] = TCON(encoding=3, text=TagHelper.__str(self.song.get_composer()))
        tags['WOAF'] = WOAF(encoding=3, text=TagHelper.__str(self.song.get_track_url()))
        tags['USLT'] = USLT(encoding=3, text=TagHelper.__str(self.song.get_lyrics()))
        tags['TEXT'] = TEXT(encoding=3, text=TagHelper.__str(self.song.get_lyrics_writer()))
        # TODO: Currently not supported song's properties: explicit, album_url, group
        i: int = self.song.get_disc_number()
        total: int = self.song.get_disc_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_disc_number()) + '/' + TagHelper.__str(self.song.get_disc_count())
            tags['TPOS'] = TPOS(encoding=3, text=c)
        i = self.song.get_track_number()
        total = self.song.get_track_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_track_number()) + '/' + TagHelper.__str(self.song.get_track_count())
            tags['TRCK'] = TRCK(encoding=3, text=c)
        # Generate the tag representation of the cover image, if defined.
        if self.song.get_cover_path() is not None:
            with open(self.song.get_cover_path(), 'rb') as cover:
                tags['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, data=cover.read())
        if Config.Config.get_watermark():
            # Add the application watermark.
            tags['COMM'] = COMM(encoding=3, text=Config.Config.get_watermark_text())
        # Save the edited tags to the file.
        tags.save()

    def __save_flac(self) -> None:
        """
        Sets the file tags according to song properties using the format required by FLAC files.
        """
        tags: Any = self.song.get_tag_object()
        # Set the tags value according to song properties.
        tags['title'] = [TagHelper.__str(self.song.get_title())]
        tags['artist'] = [TagHelper.__str(self.song.get_artist())]
        tags['albumartist'] = [TagHelper.__str(self.song.get_album_artist())]
        tags['album'] = [TagHelper.__str(self.song.get_album())]
        tags['year'] = [TagHelper.__str(self.song.get_year())]
        tags['genre'] = [TagHelper.__str(self.song.get_genre())]
        tags['composer'] = [TagHelper.__str(self.song.get_composer())]
        tags['wwwaudiofile'] = [TagHelper.__str(self.song.get_track_url())]
        tags['wwwartist'] = [TagHelper.__str(self.song.get_album_url())]
        i: int = self.song.get_disc_number()
        total: int = self.song.get_disc_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_disc_number()) + '/' + TagHelper.__str(self.song.get_disc_count())
            tags['discnumber'] = [c]
        i = self.song.get_track_number()
        total = self.song.get_track_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_track_number()) + '/' + TagHelper.__str(self.song.get_track_count())
            tags['tracknumber'] = [c]
        tags['lyrics'] = [TagHelper.__str(self.song.get_lyrics())]
        tags['lyricist'] = [TagHelper.__str(self.song.get_lyrics_writer())]
        tags['grouping'] = [TagHelper.__str(self.song.get_group())]
        # TODO: Currently not supported song's properties: explicit
        if self.song.get_cover_path() is not None:
            with open(self.song.get_cover_path(), 'rb') as cover:
                # Generate the picture object representing the cover image.
                picture = Picture()
                picture.data = cover.read()
                picture.type = PictureType.COVER_FRONT
                picture.mime = u'image/jpeg'
                picture.width = 1000
                picture.height = 1000
                picture.depth = 16
                # Remove all the pictures from this file.
                tags.clear_pictures()
                # Add the picture that has been found.
                tags.add_picture(picture)
        if Config.Config.get_watermark():
            # Add the application watermark.
            tags['comment'] = [Config.Config.get_watermark_text()]
        # Save the edited tags to the file.
        tags.save()

    def __save_aiff(self) -> None:
        """
        Sets the file tags according to specification for AIFF audio format.
        """
        # I figured out AIFF files use ID3 tags as well as MP3 do.
        self.__save_id3()
        return

    def __save_ogg(self) -> None:
        """
        Sets the file tags according to the standard used in OGG files.
        """
        tags: Any = self.song.get_tag_object()
        # Set the tags value according to song properties.
        tags['title'] = [TagHelper.__str(self.song.get_title())]
        tags['artist'] = [TagHelper.__str(self.song.get_artist())]
        tags['albumartist'] = [TagHelper.__str(self.song.get_album_artist())]
        tags['album'] = [TagHelper.__str(self.song.get_album())]
        tags['year'] = [TagHelper.__str(self.song.get_year())]
        tags['genre'] = [TagHelper.__str(self.song.get_genre())]
        tags['composer'] = [TagHelper.__str(self.song.get_composer())]
        tags['wwwaudiofile'] = [TagHelper.__str(self.song.get_track_url())]
        tags['wwwartist'] = [TagHelper.__str(self.song.get_album_url())]
        i: int = self.song.get_disc_number()
        total: int = self.song.get_disc_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_disc_number()) + '/' + TagHelper.__str(self.song.get_disc_count())
            tags['discnumber'] = [c]
        i = self.song.get_track_number()
        total = self.song.get_track_count()
        if i > 0 and total > 0:
            c: str = TagHelper.__str(self.song.get_track_number()) + '/' + TagHelper.__str(self.song.get_track_count())
            tags['tracknumber'] = [c]
        tags['lyrics'] = [TagHelper.__str(self.song.get_lyrics())]
        tags['lyricist'] = [TagHelper.__str(self.song.get_lyrics_writer())]
        tags['grouping'] = [TagHelper.__str(self.song.get_group())]
        if self.song.get_cover_path() is not None:
            with open(self.song.get_cover_path(), 'rb') as cover:
                # Encode the image as Base64 string.
                tags['METADATA_BLOCK_PICTURE'] = str(base64.b64encode(cover.read()))
        if Config.Config.get_watermark():
            # Add the application watermark.
            tags['comment'] = [Config.Config.get_watermark_text()]
        tags.save()

    @staticmethod
    def get_supported_formats() -> Set[str]:
        """
        Returns the extensions of all the supported file types.
        :return: A set containing the supported file extensions.
        :rtype: Set[str]
        """
        return TagHelper.SUPPORTED_FORMATS

    @staticmethod
    def generate_tag_object(song: Song) -> Any:
        """
        Generates the object that allows to handle the tags embedded in the audio file.
        :param song: An instance of the class "Song" representing the audio file to process.
        :type song: Song
        :return: An object representing the song's tags.
        :rtype: Any
        :raise ValueError: If an unsupported file type has been defined in the song object.
        """
        extension: str = song.get_extension()
        path: str = song.get_path()
        if not extension or not path:
            return None
        if extension == 'm4a':
            # Generate the object to process some MPEG based files such as Apple ALAC.
            return MP4(path)
        if extension == 'mp3':
            # Generate the object to process MP3 and similar formats.
            return ID3(path)
        elif extension == 'flac':
            # Generate the object to process FLAC encoded files.
            return FLAC(path)
        elif extension == 'aif' or extension == 'aiff':
            # Generate the object to process AIFF encoded files.
            return AIFF(path)
        elif extension == 'ogg':
            # Generate the object to process OGG files.
            return mutagen.File(path)
        else:
            raise ValueError('Unsupported file type.')

    def set_song(self, song: Song) -> None:
        """
        Sets the song that will be processed.
        :param song: An instance of the class "Song" representing the song to process.
        :type song: Song
        """
        self.song = song

    def get_song(self) -> Song:
        """
        Returns the song that will be processed.
        :return: An instance of the class "Song" representing the song to process.
        :rtype Song
        """
        return self.song

    def __init__(self, song: Song):
        """
        The class constructor.
        :param song: An instance of the class "Song" representing the audio file to process.
        :type song: Song
        """
        self.set_song(song)

    def fetch(self) -> None:
        """
        Loads the tags from the audio file defined and then set them into the song object.
        :raise ValueError: If no song has been defined.
        :raise ValueError: If an unsupported file type has been defined in the song object.
        """
        if self.song is None:
            raise ValueError('No song has been defined.')
        tags: Any = self.song.get_tag_object()
        extension: str = self.song.get_extension()
        # Load the song title and artists required to build the search query used by iTunes API and lyrics look up.
        if extension == 'm4a':
            if '©nam' in tags and len(tags['©nam']) > 0:
                self.song.set_title(tags['©nam'][0])
            if '©ART' in tags and len(tags['©ART']) > 0:
                self.song.set_artist(tags['©ART'][0])
        elif extension == 'mp3':
            if 'TIT2' in tags:
                self.song.set_title(str(tags['TIT2']))
            if 'TPE1' in tags:
                self.song.set_artist(str(tags['TPE1']))
        elif extension == 'flac':
            if 'title' in tags and len(tags['title']) > 0:
                self.song.set_title(tags['title'][0])
            if 'artist' in tags and len(tags['artist']) > 0:
                self.song.set_artist(tags['artist'][0])
        elif extension == 'aif' or extension == 'aiff':
            if 'TIT2' in tags:
                self.song.set_title(str(tags['TIT2']))
            if 'TPE1' in tags:
                self.song.set_artist(str(tags['TPE1']))
        elif extension == 'ogg':
            if 'title' in tags and len(tags['title']) > 0:
                self.song.set_title(tags['title'][0])
            if 'artist' in tags and len(tags['artist']) > 0:
                self.song.set_artist(tags['artist'][0])
        else:
            raise ValueError('Unsupported file type.')

    def save(self) -> None:
        """
        Sets the file tags according to song properties.
        """
        if self.song is None:
            raise ValueError('No song has been defined.')
        extension: str = self.song.get_extension()
        if extension == 'm4a':
            self.__save_m4a()
        elif extension == 'mp3':
            self.__save_id3()
        elif extension == 'flac':
            self.__save_flac()
        elif extension == 'aif' or extension == 'aiff':
            self.__save_aiff()
        elif extension == 'ogg':
            self.__save_ogg()
        else:
            raise ValueError('Unsupported file type.')
