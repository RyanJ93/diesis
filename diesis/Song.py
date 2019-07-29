from urllib import request, parse
from urllib.error import HTTPError
from datetime import *
from hashlib import md5
from typing import List, Dict, Any, Optional
import json
import re
import os
import tempfile
from diesis import LyricsFinder, Logger, Config, TagHelper, Converter, Utils


class Song:
    __QUERY_FILTERS: List[str] = [r'\[[\S\s]+\]', r'\(radio\s+edit\)', r'^[0-9]+\.?']

    original_path: str = None
    path: str = None
    extension: str = None
    query: str = None
    minimal_query: str = None
    tags: Any = None
    tag_helper: TagHelper.TagHelper = None
    query_accuracy: int = 0
    title: str = None
    artist: str = None
    album_artist: str = None
    album: str = None
    cover_url: str = None
    cover_path: str = None
    date: str = None
    year: int = None
    disc_count: int = 0
    disc_number: int = 0
    track_count: int = 0
    track_number: int = 0
    genre: str = None
    group: str = None
    composer: str = None
    explicit: bool = False
    album_url: str = None
    track_url: str = None
    lyrics: str = None
    lyrics_writer: str = None
    found: bool = False

    def __load_tags(self) -> None:
        """
        Loads the song title and author embedded in file tags.
        :raise ValueError: If an unsupported file has been defined.
        """
        self.tags = TagHelper.TagHelper.generate_tag_object(self)
        self.tag_helper = TagHelper.TagHelper(self)
        self.tag_helper.fetch()

    @staticmethod
    def __filter_itunes_results(data: List[Dict[str, str]], query: str) -> int:
        """
        Analyzes results returned by iTunes and returns the index to the closest results according to song metadata.
        :param data: A list containing all the results returned by iTunes APIs.
        :type data: List[Dict[str, str]]
        :param query: A string containing the original query used to find song information through iTunes.
        :type query: str
        :return: An integer number representing the index of the closes entry found.
        :rtype: int
        """
        # Split the search query into words.
        words: List[str] = re.findall(r'[\w\']+', query.lower())
        max_score: int = 0
        min_length: int = 0
        index: int = 0
        i: int = 0
        # Check each result.
        for result in data:
            # Get all the words contained i the title according to iTunes.
            title_words: List[str] = re.findall(r'[\w\']+', result['trackName'].lower())
            title_length: int = len(title_words)
            # Find the common words between the words contained in the query and the words contained in this title.
            score: int = len(list(set(title_words) & set(words)))
            if score > max_score and (min_length == 0 or title_length < min_length):
                # Find the element having the highest number of matching words but the lowest length.
                index = i
                max_score = score
                min_length = title_length
            i += 1
        return index

    def __set_info_from_itunes(self, data: Any, query: str) -> None:
        """
        Loads information about this track from the most eligible result returned by the iTunes API.
        :param data: The whole response returned by iTunes.
        :type data: Any
        :param query: A string representing the search query used to get such information.
        :type query: str
        """
        if data['resultCount'] == 0:
            return
        Logger.Logger.log('Processing metadata from iTunes...')
        index: int = 0
        if data['resultCount'] != 1 and not Config.Config.get_strict_meta():
            Logger.Logger.log('Multiple results returned by iTunes, filtering them...')
            index = Song.__filter_itunes_results(data['results'], query)
        data = data['results'][index]
        # Add support for album artist and composer.
        self.title = data['trackName']
        self.artist = data['artistName']
        self.album_artist = data['artistName']
        self.genre = data['primaryGenreName']
        self.album = data['collectionName']
        release_date: datetime = datetime.strptime(data['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')
        self.year = release_date.year
        self.cover_url = data['artworkUrl100'].replace('100x100bb.jpg', '1000x1000bb.jpg')
        self.disc_count = data['discCount']
        self.disc_number = data['discNumber']
        self.track_count = data['trackCount']
        self.track_number = data['trackNumber']
        # TODO: Currently iTunes doesn't support information about group and composer.
        # self.group = data['artistName']
        # self.composer = data['artistName']
        if data['trackExplicitness'] == 'explicit':
            self.explicit = True
        else:
            self.explicit = False
        self.album_url = data['artistViewUrl']
        self.track_url = data['trackViewUrl']

    def __get_filter_regex(self) -> str:
        """
        Returns the regex used to filter out unnecessary information from the simplified search query version.
        :return: A string containing the regular expression.
        :rtype: str
        """
        return '(' + ')|('.join(self.__QUERY_FILTERS) + ')'

    def __generate_search_query(self) -> None:
        """
        Generates the search query based on available information for this song.
        """
        if self.query_accuracy < 100:
            if self.title is not None and self.title != '' and self.artist is not None and self.artist != '':
                # Use the title and the artist name to find more information about the song.
                query: str = self.title + ' ' + self.artist
                query = re.sub(self.__get_filter_regex(), '', query)
                self.query = query
                # Remove unnecessary information in order to get a simpler query version.
                self.minimal_query = re.sub(r'\([\s\S]+\)', '', query).strip()
                self.query_accuracy = 100
                return
        if self.query_accuracy < 50:
            # No title nor artist name available, use the filename as search query.
            filename: str = os.path.basename(self.original_path)
            filename = os.path.splitext(filename)[0]
            query: str = filename.lower()
            query = re.sub(self.__get_filter_regex(), '', query)
            query = query.replace('_', ' ')
            query = query.strip()
            self.query = query
            self.minimal_query = re.sub(r'\([\s\S]+\)', '', query).strip()
            self.query_accuracy = 50

    def __init__(self, path: str, original_path: Optional[str] = None):
        """
        The class constructor.
        :param path: A string containing the path to the song file.
        :type path: str
        :param original_path: A string containing the original path, if the file has been moved.
        :type original_path: Optional[str]
        """
        if path:
            self.set_path(path, original_path)

    def get_tag_object(self) -> Any:
        """
        Returns the object that manages the song's tags.
        :return: An instance of the class that changes according to the audio file type.
        :rtype: Any
        """
        return self.tags

    def set_path(self, path: str, original_path: Optional[str] = None) -> None:
        """
        Sets the path to the song file.
        :param path: A string containing the path to the song file.
        :type path: str
        :param original_path: A string containing the original path, if the file has been moved.
        :type original_path: Optional[str]
        :raise ValueError: If an empty path is given.
        """
        if not path:
            raise ValueError('Path cannot be empty.')
        self.path = path
        if original_path:
            self.original_path = original_path
        else:
            self.original_path = path
        self.extension = os.path.splitext(path)[1].lower()[1:]
        # Reload tags according to new file.
        self.__load_tags()
        self.__generate_search_query()

    def get_path(self) -> Optional[str]:
        """
        Returns the path to the song file.
        :return: A string containing the path to the song file or "None" if no path has been defined.
        :rtype: Optional[str]
        """
        return self.path

    def get_original_path(self) -> Optional[str]:
        """
        Returns the path to the original file rather than its temporary copy.
        :return: A string containing the original path to the song file or "None" if no path has been defined.
        :rtype: Optional[str]
        """
        return self.original_path

    def get_extension(self) -> Optional[str]:
        """
        Returns the extension detected from the song filename.
        :return: A string containing the extension or "None" if no path has been defined.
        :rtype: Optional[str]
        """
        return self.extension

    def get_query_accuracy(self) -> int:
        """
        Returns the accuracy according to the search query that has been generated based on song's information.
        :return: An integer number representing the query accuracy from 0 (no query generated) to 100 (max accuracy).
        :rtype: int
        """
        return self.query_accuracy

    def set_title(self, title: str) -> None:
        """
        Sets the song title.
        :param title: A string containing the song title.
        :type title: str
        """
        self.title = title
        # Rebuild the song's search query to include the title defined.
        self.query_accuracy = 0
        self.__generate_search_query()

    def get_title(self) -> Optional[str]:
        """
        Returns the song title.
        :return: A string containing the song title, if no title has been defined nor found, "None" will be returned.
        :rtype: Optional[str]
        """
        return self.title

    def set_artist(self, artist: str) -> None:
        """
        Sets the song artist.
        :param artist: A string containing the artist, if no artist has been defined nor found, "None" will be returned.
        :type artist: str
        """
        self.artist = artist
        # Rebuild the song's search query to include the artist defined.
        self.query_accuracy = 0
        self.__generate_search_query()

    def get_artist(self) -> Optional[str]:
        """
        Returns the song artist.
        :return: A string containing the song artist, if no artist has been defined nor found, "None" will be returned.
        :rtype: Optional[str]
        """
        return self.artist

    def set_lyrics_writer(self, lyrics_writer: str) -> None:
        """
        Returns the author of the song's lyrics.
        :param lyrics_writer: A string containing the name(s) of the authors separated by a comma.
        :type lyrics_writer: str
        """
        self.lyrics_writer = lyrics_writer

    def get_lyrics_writer(self) -> Optional[str]:
        """
        Returns the author of the song's lyrics.
        :return: A string containing the name(s) of the authors, if no author has been found, will be returned None.
        :rtype: Optional[str]
        """
        return self.lyrics_writer

    def set_genre(self, genre: str) -> None:
        """
        Sets the song genre.
        :param genre: A string representing the song genre.
        :type genre: str
        """
        self.genre = genre

    def get_genre(self) -> Optional[str]:
        """
        Returns the song genre.
        :return: A string representing the song genre.
        :rtype: str
        """
        return self.genre

    def set_group(self, group: str) -> None:
        """
        Sets the name of the group who performed this song.
        :param group: A string containing the group name.
        :type group: str
        """
        self.group = group

    def get_group(self) -> Optional[str]:
        """
        Returns the name of the group who performed this song.
        :return: A string containing the group name.
        :rtype: str
        """
        return self.group

    def set_composer(self, composer: str) -> None:
        """
        Sets the name of the composer who wrote this song.
        :param composer: A string containing the composer name.
        :type composer: str
        """
        self.composer = composer

    def get_composer(self) -> Optional[str]:
        """
        Returns the name of the composer who wrote this song.
        :return: A string containing the composer name.
        :rtype: str
        """
        return self.composer

    def set_explicit(self, explicit: bool) -> None:
        """
        Marks this song as explicit or clear.
        :param explicit: If set to "True" the song will be marked as explicit, otherwise it will be considered clear.
        :type explicit: bool
        """
        self.explicit = explicit

    def get_explicit(self) -> bool:
        """
        Returns if the song has been marked as explicit or clear.
        :return: If the song has been marked as explicit will be returned "True", otherwise "False".
        :rtype: bool
        """
        return self.explicit

    def set_album_url(self, album_url: str) -> None:
        """
        Sets the URL to the album page on the iTunes website.
        :param album_url: A string containing the iTunes URL.
        :type album_url: str
        """
        self.album_url = album_url

    def get_album_url(self) -> Optional[str]:
        """
        Returns the URL to the album page on the iTunes website.
        :return: A string containing the iTunes URL.
        :rtype: str
        """
        return self.album_url

    def set_track_url(self, track_url: str) -> None:
        """
        Sets the URL to the song page on the iTunes store.
        :param track_url: A string containing the URL.
        :type track_url: str
        """
        self.track_url = track_url

    def get_track_url(self) -> Optional[str]:
        """
        Returns the URL to the song page on the iTunes store.
        :return: A string containing the URL.
        :rtype: str
        """
        return self.track_url

    def set_lyrics(self, lyrics: str) -> None:
        """
        Sets the song lyrics.
        :param lyrics: A string containing the full song lyrics.
        :type lyrics: str
        """
        self.lyrics = lyrics

    def get_lyrics(self) -> Optional[str]:
        """
        Returns the song lyrics.
        :return: A string containing the lyrics, if no lyrics were found, None will be returned instead.
        :rtype: Optional[str]
        """
        return self.lyrics

    def set_album_artist(self, album_artist: str) -> None:
        """
        Sets the artist of the whole album where this song is contained in.
        :param album_artist: A string containing the artist.
        :type album_artist: str
        """
        self.album_artist = album_artist

    def get_album_artist(self) -> Optional[str]:
        """
        Returns the artist of the whole album where this song is contained in.
        :return: A string containing the album artist, if no artist has been defined, "None" will be returned instead.
        :rtype: Optional[str]
        """
        return self.album_artist

    def set_album(self, album: str) -> None:
        """
        Sets the name of the album where this song is contained in.
        :param album: A string representing the album name.
        :type album: str
        """
        self.album = album

    def get_album(self) -> Optional[str]:
        """
        Returns the name of the album where this song is contained in.
        :return: A string containing the album name, if no album has been defined, "None" will be returned instead.
        :rtype: Optional[str]
        """
        return self.album

    def set_cover_path(self, path: str) -> None:
        """
        Sets the cover picture for this song.
        :param path: A string containing the path to the image file to use.
        :type path: str
        """
        self.cover_path = path
        # The cover URL is no longer required as a custom cover has been defined.
        self.cover_url = None

    def get_cover_path(self) -> Optional[str]:
        """
        Returns the path to the song cover image.
        :return: A string containing the path to the image, if no image has been defined, "None" will be returned.
        :rtype: Optional[str]
        """
        return self.cover_path

    def get_cover_url(self) -> Optional[str]:
        """
        Returns the URL of the image that has been found using the iTunes API.
        :return: A string containing the URL, if no image was found, "None" will be returned instead.
        :rtype: Optional[str]
        """
        return self.cover_url

    def set_year(self, year: int) -> None:
        """
        Sets the year when this song was made.
        :param year: An integer number greater than zero representing the year.
        :type year: int
        """
        if year <= 0:
            # Seriously, are you trying to convince me this song was made before Christ?
            self.year = None
            return
        self.year = year

    def get_year(self) -> Optional[int]:
        """
        Returns the year when this song was made.
        :return: An integer number representing the year, if no year has been defined, "None" will be returned.
        :rtype: Optional[int]
        """
        return self.year

    def set_disk(self, number: int, count: int) -> None:
        """
        Sets information about discs.
        :param number: An integer number greater than zero representing the number of the disc where this song is.
        :type number: int
        :param count: An integer number greater than zero representing the total number of discs.
        :type count: int
        """
        if count and count > 0:
            self.disc_count = count
        else:
            self.disc_count = None
        if number and number > 0:
            if self.disc_count and number > self.disc_count:
                # The disc number cannot be greater than the total disc number.
                self.disc_number = self.disc_count
            self.disc_number = number
            return
        self.disc_number = None

    def get_disc_count(self) -> Optional[int]:
        """
        Returns the total number of disc that compose the album where this song has been released in.
        :return: An integer number greater than zero representing the number or None if no information is available.
        :rtype: Optional[int]
        """
        return self.disc_count

    def get_disc_number(self) -> Optional[int]:
        """
        Returns the number of the disk where this song has been released in.
        :return: An integer number greater than zero representing the disc number or None if no number has been defined.
        :rtype: Optional[int]
        """
        return self.disc_number

    def set_track(self, number: int, count: int) -> None:
        """
        Sets information about tracks.
        :param number: An integer number greater than zero representing the track number of this song within the disc.
        :type number: int
        :param count: An integer number greater than zero representing the total number of tracks.
        :type count: int
        """
        if count and count > 0:
            self.track_count = count
        else:
            self.track_count = None
        if number and number > 0:
            if self.track_count and number > self.track_count:
                # The track number cannot be greater than the total track number.
                self.track_number = self.track_count
            self.track_number = number
            return
        self.track_number = None

    def get_track_count(self) -> Optional[int]:
        """
        Returns the track number of this song within the disc where this song is contained in.
        :return: An integer number greater than zero representing the track number or None if it is not available.
        :rtype: Optional[int]
        """
        return self.track_count

    def get_track_number(self) -> Optional[int]:
        """
        Returns the total count of tracks contained in the disk where this song has been released in.
        :return: An integer number greater than zero representing the number of track or None if it is not available.
        :rtype: Optional[int]
        """
        return self.track_number

    def is_found(self) -> bool:
        """
        Checks if online information for this song have been found or not.
        :return: If online information were found will be returned "True".
        :rtype: bool
        """
        return self.found

    def get_query(self, minimal: bool = False) -> Optional[str]:
        """
        Returns the search query generated for this song and used while looking up information through iTunes.
        :param minimal: If set to "True" the simpler search query version will be returned instead of the complete one.
        :type minimal: bool
        :return: A string containing the search query generated, if no query has been generated, "None" is returned.
        :rtype: Optional[str]
        """
        if minimal:
            return self.minimal_query
        return self.query

    def fetch_info(self, minimal: bool = False) -> None:
        """
        Fetch song information from the iTunes APIs based on the generated search query.
        :param minimal: If set to "True" the simpler search query version will be used instead of the complete one.
        :type minimal: bool
        :raise RuntimeError: If no song file has been defined.
        """
        self.found = False
        query: str = self.get_query(minimal)
        if not query:
            raise RuntimeError('No song has been defined.')
        # Prepare the API call.
        params: str = 'country=US&entity=song&limit=10&version=2&explicit=Yes&media=music'
        url: str = 'https://itunes.apple.com/search?term=' + parse.quote_plus(query) + '&' + params
        try:
            # Send the request and load the returned contents.
            req = request.Request(url, headers={
                'User-Agent': Config.Config.get_user_agent()
            })
            response = request.urlopen(req)
            contents: str = response.read().decode('utf-8')
        except (HTTPError, TimeoutError) as ex:
            Logger.Logger.log_error(str(ex))
            Logger.Logger.log_error('Request failed for URL: ' + url)
            return
        # Parse the response from the endpoint as a JSON encoded string
        data: Any = json.loads(contents)
        if data['resultCount'] == 0:
            title: str = Utils.Utils.str(self.title)
            Logger.Logger.log('Song ' + title + ' not found (query: ' + Utils.Utils.str(self.query) + ').')
            return
        # Update the song properties according to information returned by iTunes.
        self.__set_info_from_itunes(data, query)
        self.found = True
        if self.query_accuracy < 100:
            # If query accuracy was not the best, reprocess it using new information.
            self.__generate_search_query()

    def fetch_cover(self) -> None:
        """
        Fetches the cover image according to the URL returned by iTunes API.
        """
        self.cover_path = None
        if self.cover_url is None:
            Logger.Logger.log('No cover picture found for this song.')
            return
        Logger.Logger.log('Retrieving cover picture from iTunes...')
        url_hash: str = md5(self.cover_url.encode('utf-8')).hexdigest()
        filename: str = tempfile.gettempdir() + url_hash + '.jpg'
        try:
            request.urlretrieve(self.cover_url, filename)
            self.cover_path = filename
        except (HTTPError, TimeoutError) as ex:
            Logger.Logger.log_error(str(ex))
            Logger.Logger.log_error('Request failed for URL: ' + Utils.Utils.str(self.cover_url))
            self.cover_path = None

    def fetch_lyrics(self) -> None:
        """
        Fetches the song lyrics from the supported providers.
        """
        if self.artist is None or self.title is None:
            return
        Logger.Logger.log('Looking for song lyrics...')
        finder = LyricsFinder.LyricsFinder(self)
        finder.fetch()
        self.lyrics = finder.get_lyrics()
        self.lyrics_writer = finder.get_lyrics_writer()
        if not self.lyrics:
            Logger.Logger.log('No lyrics found for this song.')

    def get_all_info(self) -> None:
        """
        Fetches information about meta tags, cover picture and lyrics based on the song defined.
        """
        self.fetch_info(False)
        if not self.found and not Config.Config.get_strict_meta():
            Logger.Logger.log('No iTunes data found using full song name, retrying using a shorter version...')
            self.fetch_info(True)
        if not self.found:
            Logger.Logger.log('No available data for this song, skipping it...')
            return
        self.fetch_cover()
        self.fetch_lyrics()

    def convert(self, conversion_format: str) -> None:
        """
        Converts the song into the given format.
        :param conversion_format: A string containing the format the song must be converted into.
        :type conversion_format: str
        """
        if self.extension == conversion_format:
            return
        Logger.Logger.log('Converting the song into ' + conversion_format)
        converter: Converter.Converter = Converter.Converter(self)
        # Convert the file into the given format.
        new_path: str = converter.convert(conversion_format)
        if os.path.exists(self.path):
            os.remove(self.path)
        # Update the path and reload tags according to new file generated.
        self.set_path(new_path, self.original_path)

    def save(self) -> None:
        """
        Saves all the properties defined in this class instance to the file represented by this object.
        """
        if not self.found:
            return
        self.tag_helper.save()
