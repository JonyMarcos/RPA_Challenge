import os
import datetime
from RPA.Excel.Files import Files
from robocorp.tasks import task

def get_output_filename():
    # Gerar nome do arquivo de saída com base na data e hora atual.
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
    lib = Files()
    lib.create_workbook()
    sheet = lib.create_worksheet()

    # Verificar se a planilha foi criada corretamente
    if not sheet:
        print("Error: Worksheet creation failed")
        return None

    # Define the headers
    headers = ["Search phrase", "Title", "Date", "Description", "Image URL", "Title Search Count", "Description Search Count", "Title Contains Money", "Description Contains Money"]
    print("Headers:", headers)
    sheet.append_rows_to_worksheet([headers])

    # Write the data
    for news_item in data:
        row_data = [
            news_item["Search phrase"],
            news_item["Title"],
            news_item["Date"],
            news_item["Description"],
            news_item["Image URL"],
            news_item["Title Search Count"],
            news_item["Description Search Count"],
            news_item["Title Contains Money"],
            news_item["Description Contains Money"]
        ]
        print("Row data:", row_data)
        sheet.append_rows_to_worksheet([row_data])

    # Save the Excel file to the specified path
    lib.save_workbook(output_path)

    return output_path  # Return the saved file path