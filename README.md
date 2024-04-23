# RPA Challenge 3.0

## Overview
This Robotic Process Automation (RPA) project automates the task of fetching the latest news articles from the Gothamist newspaper based on predefined search phrases. It utilizes the Robocorp platform and Python programming language to execute the automation tasks.

## Features
- Searches news articles on Gothamist using predefined search phrases.
- Extracts information such as title, date, description, image URL, and search counts.
- Utilizes Robocorp's workitems for input data instead of an Excel file.
- Stores the extracted data in an Excel file for further analysis.

## Requirements
- Python 3.10.x
- robocorp-truststore 0.8.0
- rpaframework 28.5.1
- robocorp 1.6.2
- robocorp-browser 2.2.2
- robocorp-excel 0.4.2
- requests 2.31.0
- openpyxl 3.2.0b1

## Usage
1. Clone or download the repository from [GitHub](https://github.com/JonyMarcos/RPA_Challenge).
2. Navigate to the project directory.
3. Create and activate a Conda environment with the project dependencies using the `conda.yaml` file:
4. Ensure that the Robocorp Workforce Agent is installed and configured on your system.
5. Execute the automation task using the `task.py` script:
rcc run --file task.py
6. The RPA will fetch the latest news articles for each search phrase provided in the workitems and store the extracted data in an Excel file named `gothamist_news_data.xlsx` in the `output` directory.

## Contributors
- [João Marcos Cruz](https://github.com/JonyMarcos)
