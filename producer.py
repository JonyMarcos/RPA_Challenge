from typing import List

from robocorp import excel, workitems
from robocorp.tasks import task
from robocorp.excel.tables import Table

# Define the input file name
INPUT_FILE_NAME = 'input.xlsx'

@task
def split_file():
    # Get the current work item
    item = workitems.inputs.current
    
    # Get the path of the input file from the work item
    path = item.get_file(INPUT_FILE_NAME)

    # Open the workbook and read the worksheet as a table
    workbook = excel.open_workbook(path)
    worksheet = workbook.worksheet("news")
    table = worksheet.as_table(header=True)

    # Group the table by the 'Name' column
    groups: List[Table] = table.group_by_column('Name')

    # List to store the grouped names
    names_list = []

    # Iterate over the groups and extract names
    for products in groups:
        rows: List[dict] = products.to_list()
        for row in rows:
            names_list.append(row['Name'])

    # Create the output with the grouped names in a single list
    if names_list:
        payload = {"index": 0, "Name": names_list}
        workitems.outputs.create(payload=payload)
