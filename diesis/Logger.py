from diesis import Config
from typing import Optional
from datetime import datetime


class Logger:
    __log_fp = None

    @staticmethod
    def log(message: str) -> None:
        """
        Displays a message to the user console.
        :param message: A string containing the message to show.
        :type message: str
        """
        if message and Config.Config.is_verbose():
            print(message)
        log_file: Optional[str] = Config.Config.get_log_file()
        if message and log_file:
            if not Logger.__log_fp:
                # Open the log file if no file pointer has been found.
                Logger.__log_fp = open(log_file, 'a')
            date: str = datetime.today().strftime('%Y/%m/%d - %H:%M:%S')
            message = '[' + date + ']: ' + message + '\n'
            # Write log message to file including current date.
            Logger.__log_fp.write(message)

    @staticmethod
    def log_error(message: str) -> None:
        """
        Displays an error message to the user console, error messages are yellow colored.
        :param message: A string containing the error message to show.
        :type message: str
        """
        if message and Config.Config.is_verbose():
            print('\033[93m' + message + '\033[0m')
