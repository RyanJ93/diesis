from typing import Any


class Utils:
    @staticmethod
    def str(value: Any) -> str:
        """
        Converts a given variable into a string representation.
        :param value: The variable to be converted.
        :type value: Any
        :return: The string representation of the given variable.
        :rtype: str
        """
        if value is None:
            return ''
        return str(value)
