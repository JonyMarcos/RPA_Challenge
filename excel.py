import os
import datetime
import openpyxl

def get_output_filename():
    now = datetime.datetime.now()
    timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
    filename = f"output_{timestamp}.xlsx"
    return filename

def write_to_excel(data, output_dir):
    # Obter o nome do arquivo com base na data e hora atual
    filename = get_output_filename()
    # Construir o caminho completo do arquivo
    output_path = os.path.join(output_dir, filename)

    # Criar um novo arquivo Excel
    wb = openpyxl.Workbook()
    sheet = wb.active

    # Definir os cabeçalhos
    headers = ["Title", "Date", "Description", "Image URL", "Title Search Count", "Description Search Count", "Title Contains Money", "Description Contains Money"]
    sheet.append(headers)

    # Escrever os dados
    sheet.append(data)

    # Salvar o arquivo Excel no caminho especificado
    wb.save(output_path)

    return output_path  # Retornar o caminho do arquivo salvo
