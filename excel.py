import os
import datetime
import openpyxl

def get_output_filename():
    # Generate output filename based on current date and time.
    now = datetime.datetime.now()
    timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
    filename = f"excel_output_{timestamp}.xlsx"
    return filename

def write_to_excel(data, output_dir):
    # Write data to an Excel file.
    filename = get_output_filename()
    # Construct the full file path
    output_path = os.path.join(output_dir, filename)

    # Create a new Excel file
    wb = openpyxl.Workbook()
    sheet = wb.active

    # Define the headers
    headers = ["Search phrase", "Title", "Date", "Description", "Image URL", "Title Search Count", "Description Search Count", "Title Contains Money", "Description Contains Money"]
    sheet.append(headers)

    # Write the data
    for news_item in data:
        sheet.append(news_item)

    # Save the Excel file to the specified path
    wb.save(output_path)

    return output_path  # Return the saved file path
