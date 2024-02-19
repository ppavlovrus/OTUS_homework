import collections
from datetime import datetime
import gzip
import json
import os
import re
import sys
from src.config import parse_config
from decimal import Decimal, ROUND_DOWN
from src.logger import setup_logger
from tqdm import tqdm
import statistics

not_parsed_threshold = 50
logger = setup_logger()

nginx_log_pattern = re.compile(
    r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+[0-9A-Za-z \-]+\[.*\] '
    r'"[A-Z]+ ([^\s\\]*) [^\s]* [0-9]* [0-9]*.* ([0-9\.]+$)')

log_file_name_pattern = re.compile(r'nginx-access-ui\.log-(\d{8})(\.gz)?$')


def find_most_recent_log_file(directory):
    try:
        files_in_directory = os.listdir(directory)
        valid_files = []

        for file_name in files_in_directory:
            if log_file_name_pattern.match(file_name):
                valid_files.append(file_name)

        if valid_files:
            dates = [datetime.strptime(log_file_name_pattern.match(f).group(1), '%Y%m%d') for f in valid_files]
            most_recent_date = max(dates)
            most_recent_file = 'nginx-access-ui.log-' + most_recent_date.strftime('%Y%m%d')

            if most_recent_file + '.gz' in valid_files:
                return most_recent_file + '.gz'
            else:
                return most_recent_file

    except FileNotFoundError as e:
        logger.error(f"Could not find last log file at path: {directory} with exception {e}")
    except IOError as e:
        logger.error(f"IOError occurred during finding las log file: {e}")


def get_requests_time_from_logs(file_path, percent_of_error_lines, processed_files_storage):
    def file_reader(f, percent_of_errors, file_size_bytes):
        error_string_size = 0
        for line_from_file in f:
            match_from_line = nginx_log_pattern.match(line_from_file)
            if match_from_line:
                yield match_from_line.group(1), Decimal(match_from_line.group(2))
            else:
                encoded = line_from_file.encode("utf-8")
                error_string_size += len(encoded)
        if (error_string_size * 100) / file_size_bytes > percent_of_errors:
            logger.error("Most part of file wasn't parsed!")

    try:
        with open(processed_files_storage, 'a') as processed:
            processed.write(file_path)
        file_size = os.path.getsize(file_path)
        opener = gzip.open(file_path, 'rt') if file_path.endswith('.gz') else open(file_path, 'r')
        with opener as log_file:
            for result in tqdm(file_reader(log_file, percent_of_error_lines, file_size), desc="Processing log file",
                               unit=" lines"):
                yield result
    except FileNotFoundError as e:
        logger.error(f"Could not find file at path: {file_path} with exception {e}")
    except IOError as e:
        logger.error(f"Error opening file at path: {file_path} with exception {e}")


def create_url_dict(filtered_log: (str, Decimal)):
    two_places = Decimal(10) ** -2
    # Handling situation with new URL
    dict_input = collections.defaultdict(
        lambda: [0, Decimal(0), Decimal(0), Decimal(0),
                 Decimal(0), Decimal(0), [], Decimal(0)]
    )
    number_of_requests = 0
    total_time_of_requests = Decimal(0)

    for url, time in filtered_log:
        number_of_requests += 1
        total_time_of_requests += time

        url_data = dict_input[url]
        # Total Requests for this URL
        url_data[0] += 1
        # Total request time for this URL
        url_data[2] += time
        # Average request time
        url_data[4] = Decimal(url_data[2] / url_data[0])
        # Maximum request time
        url_data[5] = max(url_data[5], time)
        # Add request time to list with requests time for this particular URL
        url_data[6].append(time)

    # Now we re-iterate our dictionary and calculate values
    dictionary_iterator = iter(dict_input.items())
    for _ in dict_input:
        key, value = next(dictionary_iterator)
        # Percentile from all requests
        value[1] = Decimal(value[0] * 100 / number_of_requests).quantize(two_places, ROUND_DOWN)
        # Percentile from all requests time
        value[3] = Decimal(value[2] * 100 / total_time_of_requests).quantize(two_places, ROUND_DOWN)
        # Average request time
        value[4] = Decimal(value[2] / value[0])
        value[6].sort()
        value[7] = statistics.median(value[6])
        value.pop(6)

    return dict_input


def dict_to_json(dictionary):
    json_data = []

    for key, value in dictionary.items():
        record = {"url": key, "count": value[0],
                  "count_perc": float(value[1]),
                  "time_sum": float(value[2]),
                  "time_perc": float(value[3]),
                  "time_avg": float(value[4]),
                  "time_max": float(value[5]),
                  "time_med": float(value[6])}
        json_data.append(record)
    return json_data


def insert_json_into_html(json_data, template_file_path, output_file_path):
    logger.info(f"Template file is {template_file_path}")
    logger.info(f"Output file is {output_file_path}")
    table_json = json.dumps(json_data, indent=4)

    try:
        with open(template_file_path, 'r') as template_file:
            template_content = template_file.readlines()
        line_number = 0
        for i, line in enumerate(template_content):
            if 'var table =' in line:
                line_number = i
                break
    except IOError:
        logger.error("Something wrong during open template")
        return
    try:
        template_content[line_number] = f"var table ={table_json};\n"
        # Write report file
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(template_content)
    except IOError:
        logger.error("Something wrong during writing report")
        return


def generate_report_filename(report_path):
    now = datetime.now()
    now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = "report_" + now_string + ".html"
    return report_path + report_filename


def check_file_already_processed(file_path, processed_files_path):
    try:
        with open(processed_files_path, 'r') as processed_files:
            contents = processed_files.read()
            if file_path in contents:
                return True
            else:
                return False
    except IOError:
        logger.error("Error during open processed files storage")
        return


def main():
    time_start = datetime.now()

    configuration = parse_config(sys.argv[1:])

    try:
        found_log_file = find_most_recent_log_file(configuration['LogDirectory'])
        if found_log_file == '':
            logger.error("No log file in log folder found")
        else:
            if check_file_already_processed(found_log_file, configuration['ProcessedFilesStorage']):
                logger.info(f"File {found_log_file} already processed, nothing to do, exit")
            else:
                dictionary_with_result = create_url_dict(
                    get_requests_time_from_logs(f'{configuration["LogDirectory"]}'
                                                f'\{found_log_file}',
                                                not_parsed_threshold,
                                                configuration['ProcessedFilesStorage']))
                result_json = dict_to_json(dictionary_with_result)
                insert_json_into_html(result_json, "report_template.html",
                                      generate_report_filename(configuration["ReportFile"]))

                time_stop = datetime.now()
                logger.info(f'Program started at {time_start}, stopped at {time_stop}')
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
