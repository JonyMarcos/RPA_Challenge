# RPA Challenge 3.0

## Overview
This Robotic Process Automation (RPA) project was developed as part of a selection process. It automates the task of fetching the latest news articles from the Gothamist newspaper based on predefined search phrases.

## Features
- Searches news articles on Gothamist using predefined search phrases.
- Extracts information such as title, date, description, image URL, and search counts.
- Stores the extracted data in an Excel file for further analysis.

## Requirements
- Python 3.10.12
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
  conda env create -f conda.yaml
  conda activate <environment-name>
4. Prepare an Excel file named `input.xlsx` containing the search phrases in the first column.
5. Run the `producer.py` script to generate the data:
   python producer.py
6. After successful execution of `producer.py`, run the `consumer.py` script to process the data:
  python consumer.py
7. The RPA will fetch the latest news articles for each search phrase and store the extracted data in an Excel file named `gothamist_news_data.xlsx` in the `output` directory.

## Known Issues
- Currently, the RPA can only be executed locally due to limitations in direct execution on the Robocorp platform. Efforts are underway to address this issue.

## Contributors
- [João Marcos Cruz](https://github.com/JonyMarcos)
