import os
import unittest
from decimal import Decimal
from log_analyzer import get_requests_time_from_logs, create_url_dict, dict_to_json


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
        expected_output = list(self.sample_log)
        current_folder = os.getcwd()
        actual_output = list(
            get_requests_time_from_logs(current_folder + '\\tests\\' + 'nginx-access-ui.log-20230215', 0))
        self.assertEqual(expected_output, actual_output)

    def test_create_url_dict(self):
        actual_output = create_url_dict(self.sample_log)
        self.assertEqual(self.expected_url_dict, actual_output)

    def test_dict_to_json(self):
        actual_output = dict_to_json(self.expected_url_dict)
        self.assertEqual(self.expected_json_data, actual_output)


if __name__ == '__main__':
    unittest.main()
