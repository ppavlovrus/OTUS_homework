import os
import logging
import unittest
from decimal import Decimal
from datetime import datetime
from log_analyzer import get_requests_time_from_logs, create_url_dict, \
    dict_to_json, generate_report_filename, find_most_recent_log_file, \
    check_file_already_processed
from unittest.mock import patch, mock_open


class TestLogAnalyzer(unittest.TestCase):
    # Sample log for testing
    sample_log = [
        ('/api/v2/group/', Decimal('0.05')),
        ('/export/', Decimal('1.00')),
        ('/api/v2/group/', Decimal('0.75')),
        ('/export/', Decimal('2.10')),
    ]

    # Expected result for create_url_dict
    expected_url_dict = {
        '/api/v2/group/': [2, Decimal('50.00'), Decimal('0.80'), Decimal('20.51'), Decimal('0.40'), Decimal('0.75'),
                           Decimal('0.40')],
        '/export/': [2, Decimal('50.00'), Decimal('3.10'), Decimal('79.48'), Decimal('1.55'), Decimal('2.10'),
                     Decimal('1.55')],
    }

    # Expected result for dict_to_json
    expected_json_data = [
        {"url": "/api/v2/group/", "count": 2, "count_perc": 50.00, "time_sum": 0.8, "time_perc": 20.51, "time_avg": 0.4,
         "time_max": 0.75, "time_med": 0.4},
        {"url": "/export/", "count": 2, "count_perc": 50.00, "time_sum": 3.1, "time_perc": 79.48, "time_avg": 1.55,
         "time_max": 2.1, "time_med": 1.55},
    ]

    def test_get_requests_time_from_logs(self):
        file_path = "nginx-access-ui.log-20230215"
        expected_output = list(self.sample_log)
        actual_output = list(
            get_requests_time_from_logs(file_path,
                                        50, 'processed.txt'))
        os.remove('processed.txt')
        self.assertEqual(expected_output, actual_output)

    def test_create_url_dict(self):
        actual_output = create_url_dict(self.sample_log)
        self.assertEqual(self.expected_url_dict, actual_output)

    def test_dict_to_json(self):
        actual_output = dict_to_json(self.expected_url_dict)
        self.assertEqual(self.expected_json_data, actual_output)

    @patch("log_analyzer.datetime")
    def test_generate_report_filename(self, mock_datetime):
        mock_datetime.now.return_value.strftime.return_value = '2022-04-01_00-00-00'
        result = generate_report_filename('/path/to/report/')
        expected_result = '/path/to/report/report_2022-04-01_00-00-00.html'
        self.assertEqual(result, expected_result)

    @patch('os.listdir')
    @patch('log_analyzer.log_file_name_pattern')
    @patch('log_analyzer.datetime')
    def test_find_most_recent_log_file(self, mock_datetime, mock_pattern, mock_listdir):
        mock_listdir.return_value = ['nginx-access-ui.log-20230215',
                                     'nginx-access-ui.log-20230214',
                                     'nginx-access-ui.log-20230213']

        mock_datetime.strptime.side_effect = lambda date_str, _: datetime.strptime(date_str, "%Y%m%d")

        def mock_match(file_name):
            mocked = unittest.mock.Mock()
            mocked.group.return_value = file_name.split('-')[-1]
            return mocked

        mock_pattern.match.side_effect = mock_match

        result = find_most_recent_log_file('dummy_directory')

        self.assertEqual(result, 'nginx-access-ui.log-20230215')
        mock_listdir.assert_called_once_with('dummy_directory')
        self.assertEqual(mock_pattern.match.call_count, 6)
        self.assertEqual(mock_datetime.strptime.call_count, 3)

    @patch("builtins.open", new_callable=mock_open, read_data="file1.txt\nfile2.txt\n")
    def test_file_already_processed(self, mock_file):
        logger = logging.getLogger()
        with patch.object(logger, 'error') as mock_log:
            result = check_file_already_processed("file1.txt", "processed_files.txt")
            self.assertEqual(result, True)
            self.assertEqual(mock_log.call_count, 0)

    @patch("builtins.open", new_callable=mock_open, read_data="file1.txt\nfile2.txt\n")
    def test_file_not_processed(self, mock_file):
        logger = logging.getLogger()
        with patch.object(logger, 'error') as mock_log:
            result = check_file_already_processed("file3.txt", "processed_files.txt")
            self.assertEqual(result, False)
            self.assertEqual(mock_log.call_count, 0)

    def test_with_io_error(self):
        logger = logging.getLogger()
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError
            with patch.object(logger, 'error') as mock_log:
                result = check_file_already_processed("file3.txt", "processed_files.txt")
                self.assertEqual(result, None)
                self.assertEqual(mock_log.call_count, 1)


if __name__ == '__main__':
    unittest.main()
