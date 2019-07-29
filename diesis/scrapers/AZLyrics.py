from diesis.scrapers import LyricsScraper
from urllib import parse, request
from urllib.error import HTTPError
from http.client import RemoteDisconnected
from bs4 import BeautifulSoup
from diesis import Config, Logger
from typing import Tuple, Optional


class AZLyrics(LyricsScraper.LyricsScraper):
    def __search(self, minimal: bool = False) -> str:
        """
        Finds the URL where the song lyrics is available at based on the song's query string.
        :param minimal: If set to "True", a shorter version of the song query will be used instead of the complete one.
        :type minimal: bool
        :return: A string containing the URL found, if no URL is found, and empty string will be returned instead.
        :rtype: str
        :raise ValueError: If no search query has been defined for current song.
        """
        query: str = self.get_query(minimal)
        if not query:
            raise ValueError('No query defined for this song.')
        query = parse.quote(query)
        url: str = 'https://search.azlyrics.com/search.php?q=' + query
        try:
            # Send the request to the provider website.
            req = request.Request(url, headers={
                'User-Agent': Config.Config.get_user_agent()
            })
            response = request.urlopen(req)
            contents: str = response.read().decode('utf-8')
        except (HTTPError, RemoteDisconnected, TimeoutError) as ex:
            Logger.Logger.log_error(str(ex))
            Logger.Logger.log_error('Request failed for URL: ' + url)
            return ''
        # Parse the HTML page loaded.
        document: BeautifulSoup = BeautifulSoup(contents, 'html.parser')
        main = document.select_one('table.table-condensed')
        if main is None:
            return ''
        # Find the link to the lyrics page (according to this provider, links to lyrics should be opened in a new tab,
        # then use this requirement to filter out invalid links,
        # such as pagination links that come right before real results).
        result = main.select_one('a[target="_blank"]')
        if result is None:
            return ''
        # Returns the link as a text.
        return result.get('href').strip()

    @staticmethod
    def __load(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts the song lyrics from the page that has been found in look up phase, then it will return it as a string.
        :param url: A string containing the URL where the song lyrics is located at.
        :type url: str
        :return: A tuple containing both the lyrics and its author(s) or both None if no lyrics is found.
        :rtype: Tuple[Optional[str], Optional[str]]
        :raise ValueError: If an empty URL is given.
        """
        if not str:
            raise ValueError('URL cannot be empty.')
        try:
            # Send the request to the page.
            req = request.Request(url, headers={
                'User-Agent': Config.Config.get_user_agent()
            })
            response = request.urlopen(req)
            # Load the HTML page contents.
            contents: str = response.read().decode('utf-8')
        except (HTTPError, RemoteDisconnected, TimeoutError) as ex:
            Logger.Logger.log_error(str(ex))
            Logger.Logger.log_error('Request failed for URL: ' + url)
            return None, None
        # Parse the HTML page.
        document: BeautifulSoup = BeautifulSoup(contents, 'html.parser')
        main = document.select_one('div.main-page')
        if main is None:
            return None, None
        eligible = None
        # Process each div in order to find the one containing the song lyrics.
        blocks = main.select('div')
        for element in blocks:
            if element.get('class') is None:
                eligible = element
                break
        if eligible is not None:
            # If found, return its contents as a simple text without any HTML tag.
            lyrics: str = eligible.getText().strip()
            lyrics_writer: Optional[str] = None
            # Get the element that contains the lyrics writer.
            writer_block = document.select_one('div.smt > small')
            if writer_block is not None:
                # If the element containing the author is found, get its value and format the name(s) found in it.
                lyrics_writer = writer_block.getText().strip().lower().title()
            return lyrics, lyrics_writer
        return None, None

    def fetch(self) -> None:
        """
        Searches and fetches the lyrics for the song defined.
        """
        lyrics: Tuple[Optional[str], Optional[str]] = (None, None)
        if self.query is not None:
            # If a search query for this song has been defined, search the lyrics using it.
            alternative: bool = False
            url: str = self.__search(False)
            if not url and self.minimal_query is not None and not Config.Config.get_strict_lyrics():
                # If no lyrics has been found using the normal search query, retry using a shorter and simpler one.
                Logger.Logger.log('No lyrics found using full song name, retrying using a shorter version...')
                alternative = True
                # Repeat the search telling the method to use the shorter query version.
                url = self.__search(True)
                if not url:
                    Logger.Logger.log('No lyrics found in anyway.')
            if url:
                lyrics = AZLyrics.__load(url)
                if not lyrics and not alternative and not Config.Config.get_strict_lyrics():
                    if self.minimal_query is not None:
                        # Lyrics were found but its page was empty, retry searching it using the shorter query version.
                        Logger.Logger.log('No lyrics found using full song name, retrying using a shorter version...')
                        # Repeat the search telling the method to use the shorter query version.
                        url = self.__search(True)
                        if url:
                            # Try again to fetch the song lyrics.
                            lyrics = AZLyrics.__load(url)
                        else:
                            Logger.Logger.log('No lyrics found in anyway.')
        self.lyrics = lyrics[0]
        self.lyrics_writer = lyrics[1]
