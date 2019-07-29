from diesis import FileScanner, Config


def main():
    try:
        Config.Config.setup_from_cli()
        print('Running Diesis 1.0.3')
        scanner = FileScanner.FileScanner()
        scanner.scan()
        print('All operations completed, bye!')
    except KeyboardInterrupt:
        print('Execution interrupted, bye!')
