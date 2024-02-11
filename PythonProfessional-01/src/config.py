import argparse
import configparser
import os


def parse_config(argv=None):
    # Initialize Argument Parser
    parser = argparse.ArgumentParser(description="Reads config from file")
    parser.add_argument('--config',
                        type=str,
                        required=True,
                        help='Path to the configuration file')

    # Parse Arguments
    args = parser.parse_known_args(argv)[0]

    if os.path.isfile(args.config):
        config = configparser.ConfigParser()
        config.read(args.config)

        # Return parameters
        log_directory = config.get('DEFAULT', 'LogDirectory')
        report_file = config.get('DEFAULT', 'ReportFile')

        return {"LogDirectory": log_directory, "ReportFile": report_file}

    else:
        raise Exception(f"Config file does not exist: {args.config}")
