from typing import Optional, Tuple, Any
from diesis import Song, Logger
from diesis.scrapers import AZLyrics, MusixMatch


class LyricsFinder:
    lyrics: str = None
    lyrics_writer: str = None
    song: Song = None

    def __scrape(self, provider: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Finds and fetches the song lyrics by scraping the given provider's website.
        :param provider: An integer number that allows to select the provider to scrape (1: Azlyrics, 2: MusixMatch).
        :type provider: int
        :return: A tuple containing both the lyrics and its author(s) or both None if no lyrics is found.
        :rtype: Tuple[Optional[str], Optional[str]]
        """
        scraper: Any = None
        if provider == 1:
            Logger.Logger.log('Querying "Azlyrics"...')
            scraper: AZLyrics.AZLyrics = AZLyrics.AZLyrics()
        if provider == 2:
            Logger.Logger.log('Querying "MusixMatch"...')
            scraper: MusixMatch.MusixMatch = MusixMatch.MusixMatch()
        if scraper is not None:
            scraper.set_query(self.song.get_query(False), self.song.get_query(True))
            scraper.fetch()
            return scraper.get_lyrics(), scraper.get_lyrics_writer()
        return None, None

    def set_song(self, song: Song) -> None:
        """
        Sets the song to process.
        :param song: An instance of the class "Song" representing the song.
        :type song: Song
        """
        self.song = song

    def get_song(self) -> Song:
        """
        Returns the song to process.
        :return: An instance of the class "Song" representing the song.
        :rtype: Song
        """
        return self.song

    def __init__(self, song: Song):
        """
        The class constructor.
        :param song: An instance of the class "Song" representing the song to process.
        :type song: Song
        """
        self.song = song

    def fetch(self) -> None:
        """
        Fetches the lyrics of the defined song by scraping all the available providers.
        :raise RuntimeError: If no song has been defined.
        """
        if self.song is None:
            raise RuntimeError('No song defined.')
        lyrics: Tuple[Optional[str], Optional[str]] = (None, None)
        provider: int = 1
        # Start fetching the lyrics from the first provider and go on to other ones until found.
        while not lyrics[0] and provider <= 2:
            lyrics = self.__scrape(provider)
            provider += 1
        if lyrics[0]:
            Logger.Logger.log('Song lyrics found and saved.')
        self.lyrics = lyrics[0]
        self.lyrics_writer = lyrics[1]

    def get_lyrics(self) -> Optional[str]:
        """
        Returns the lyrics found.
        :return: A string containing the lyrics found or None if no lyrics are found.
        :rtype: Optional[str]
        """
        return self.lyrics

    def get_lyrics_writer(self) -> Optional[str]:
        """
        Returns the authors who wrote the lyrics separated by a comma.
        :return: A string containing the lyrics authors, if no author is found, None will be returned instead.
        :rtype: Optional[str]
        """
        return self.lyrics_writer
