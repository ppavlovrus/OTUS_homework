import argparse
import configparser
import os


def parse_config(argv=None):
    config = {
        'LogDirectory': 'C:\\Common_Folder\\Programming\\PythonProjects\\OTUS'
                     '\\Python Professional'
                     '\\01-Advanced basics\\01_advanced_basics\\homework\\logs\\',
        'ReportFile': 'C:\\Common_Folder\\Programming\\PythonProjects\\'
                       'OTUS_homework\\PythonProfessional-01\\src'
    }
    parser = argparse.ArgumentParser(description="Reads config from file")
    parser.add_argument('--config',
                        type=str,
                        required=True,
                        help='Path to the configuration file')

    args = parser.parse_known_args(argv)[0]

    if os.path.isfile(args.config):
        config = configparser.ConfigParser()
        config.read(args.config)
        log_directory = config.get('DEFAULT', 'LogDirectory')
        report_file = config.get('DEFAULT', 'ReportFile')

        return {"LogDirectory": log_directory, "ReportFile": report_file}
    else:
        return config
