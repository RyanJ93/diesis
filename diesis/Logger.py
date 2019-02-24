from diesis import Config


class Logger:
    @staticmethod
    def log(message: str) -> None:
        """
        Displays a message to the user console.
        :param message: A string containing the message to show.
        :type message: str
        """
        if message and Config.Config.is_verbose():
            print(message)

    @staticmethod
    def log_error(message: str) -> None:
        """
        Displays an error message to the user console, error messages are yellow colored.
        :param message: A string containing the error message to show.
        :type message: str
        """
        if message and Config.Config.is_verbose():
            print('\033[93m' + message + '\033[0m')
