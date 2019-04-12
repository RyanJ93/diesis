from typing import Optional


class LyricsScraper:
    query: str = None
    minimal_query: str = None
    lyrics: str = None
    lyrics_writer: str = None

    def set_query(self, query: str, minimal_query: str) -> None:
        """
        Sets the search query to use for lyrics look up.
        :param query: A string containing the search query for this song.
        :type query: str
        :param minimal_query: A string containing a shorter query, usually it doesn't include texts inside parenthesis.
        :type minimal_query: str
        """
        self.query = query
        self.minimal_query = minimal_query

    def get_query(self, minimal: bool = False) -> str:
        """
        Returns the search query that will be used for lyrics look up.
        :param minimal: If set to "True", the shorter query version will be returned instead.
        :type minimal: bool
        :return: A string containing the search query, if no query has been defined, an empty string will be returned.
        :rtype: str
        """
        if minimal:
            query: str = self.minimal_query
        else:
            query: str = self.query
        if query is None:
            return ''
        return query

    def get_lyrics(self) -> Optional[str]:
        """
        Returns the lyrics that has been found, before using this method, you must invoke the "fetch" method.
        :return: A string containing the song lyrics found, if no lyrics were found, None will be returned.
        :rtype: Optional[str]
        """
        return self.lyrics

    def get_lyrics_writer(self) -> Optional[str]:
        """
        Returns the authors who wrote the lyrics separated by a comma.
        :return: A string containing the lyrics authors, if no author was found, None will be returned instead.
        :rtype: Optional[str]
        """
        return self.lyrics_writer
