# NGINX Log Analyzer
1. ## Installation
    To install, first make sure you have Python3 and pip on your system.
    If not, download Python3 from https://www.python.org/downloads/ and pip will be installed with it.
    
    Then, navigate to the project directory and install the dependencies with:

    ```shell
    pip install -r requirements.txt
    ```

2. ## Running the program
    To run the program, make sure you are in the same directory as your main Python script and then type:

    ```shell
    python log_analyzer.py --config <path_to_your_config_file>
    ```
    Replace `<path_to_your_config_file>` with the real path to the configuration file that your program uses.
	
3. ## Configuration file format
	
	Configuration file have following format:
		[DEFAULT]
		LogDirectory = <path_to_your_log_file>
		ReportFile = <path_to_your_report_files>
	