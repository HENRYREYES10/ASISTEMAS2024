import csv
from statistics import mean
import xlsxwriter

# Leer las respuestas del cuestionario desde el archivo CSV
file_path = 'Cuestionario_ISO27001.csv'

puntajes = {}
with open(file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    headers = next(reader)
    for row in reader:
        aspecto = row[0]
        calificaciones = row[2:7]
        puntaje = calificaciones.index('X') + 1 if 'X' in calificaciones else 0
        if aspecto not in puntajes:
            puntajes[aspecto] = []
        puntajes[aspecto].append(puntaje)

# Calcular el puntaje promedio para cada sección
promedios_por_seccion = {aspecto: mean(puntajes[aspecto]) for aspecto in puntajes}

# Crear un nuevo archivo Excel para el informe
file_path_informe = 'Informe_Cumplimiento_ISO27001.xlsx'
workbook = xlsxwriter.Workbook(file_path_informe)
worksheet = workbook.add_worksheet("Informe de Cumplimiento")

# Escribir los promedios en el nuevo archivo Excel
worksheet.write('A1', 'Aspecto Clave')
worksheet.write('B1', 'Puntaje Promedio')
row = 1
for aspecto, promedio in promedios_por_seccion.items():
    worksheet.write(row, 0, aspecto)
    worksheet.write(row, 1, promedio)
    row += 1

# Crear un gráfico de barras
chart = workbook.add_chart({'type': 'bar'})

# Configurar el gráfico
chart.add_series({
    'categories': f'=Informe de Cumplimiento!$A$2:$A${row}',
    'values': f'=Informe de Cumplimiento!$B$2:$B${row}',
    'name': 'Puntaje Promedio',
})

chart.set_title({'name': 'Informe de Cumplimiento ISO 27001'})
chart.set_x_axis({'name': 'Aspecto Clave'})
chart.set_y_axis({'name': 'Puntaje Promedio', 'major_gridlines': {'visible': False}})

worksheet.insert_chart('D5', chart)

# Guardar el archivo Excel con el informe y el gráfico
workbook.close()

print("Informe generado con éxito.")
