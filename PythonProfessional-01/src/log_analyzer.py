import collections
from datetime import datetime
import json
import os
import re
from decimal import Decimal, ROUND_DOWN
import statistics

nginx_log_pattern = re.compile(
    r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+[0-9A-Za-z \-]+\[.*\] '
    r'"[A-Z]+ ([^\s\\]*) [^\s]* [0-9]* [0-9]*.* ([0-9\.]+$)')

log_file_name_pattern = re.compile(r'nginx-access-ui\.log-(\d{8})(\.gz)?$')


def find_most_recent_log_file(directory):
    files_in_directory = os.listdir(directory)
    valid_files = []

    for file_name in files_in_directory:
        if log_file_name_pattern.match(file_name):
            valid_files.append(file_name)

    if valid_files:
        dates = [datetime.strptime(log_file_name_pattern.match(f).group(1),
                                   '%Y%m%d')
                 for f in valid_files]
        most_recent_date = max(dates)
        most_recent_file = 'nginx-access-ui.log-' + \
                           most_recent_date.strftime('%Y%m%d')

        if most_recent_file + '.gz' in valid_files:
            return most_recent_file + '.gz'
        else:
            return most_recent_file
    else:
        return None


def get_requests_time_from_logs(file_path):
    try:
        with open(file_path, 'r') as log_file:
            num = 0
            for line in log_file:
                match = nginx_log_pattern.match(line)
                num += 1
                if match:
                    yield match.group(1), Decimal(match.group(2))
    except FileNotFoundError:
        print(f"Could not find file at path: {file_path}")
        return
    except IOError:
        print(f"Error opening file at path: {file_path}")
        return


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
    table_json = json.dumps(json_data, indent=4)

    # Open the template file and read its content
    with open(template_file_path, 'r') as template_file:
        template_content = template_file.readlines()
    line_number = 0
    for i, line in enumerate(template_content):
        if 'var table =' in line:
            line_number = i
            break

    template_content[line_number] = f"var table ={table_json};\n"
    # Write report file
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(template_content)


def generate_report_filename():
    now = datetime.now()
    now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = "report_" + now_string + ".html"
    return report_filename


def main():
    time_start = datetime.now()
    file_path = 'C:\\Common_Folder\\Programming\\PythonProjects\\OTUS' \
                '\\Python Professional' \
                '\\01-Advanced basics\\01_advanced_basics\\homework\\logs' \
                '\\nginx-access-ui.log-20170630'
    d = create_url_dict(get_requests_time_from_logs(file_path))
    result_json = dict_to_json(d)
    insert_json_into_html(result_json, "report_template.html",
                          generate_report_filename())
    time_stop = datetime.now()
    print(time_stop, time_start)


if __name__ == "__main__":
    main()
