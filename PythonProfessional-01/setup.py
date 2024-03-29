from setuptools import setup

setup(
    name='nginx_log_analyzer',
    version='0.1',
    description='A log analyzer for OTUS course',
    author='Pavel Pavlov',
    author_email='ppavlovrus@gmail.com',
    packages=['src', 'tests'],
    install_requires=['tqdm==4.62.3'],
    entry_points={
        "console_scripts": [
            "nginx_log_analyzer = log_analyzer.py:main"
        ]
    }
)
