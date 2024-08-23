import pandas as pd
import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import datetime
from collections import Counter

# Función para leer los logs desde un archivo de Excel
def leer_logs_excel(file):
    try:
        df = pd.read_excel(file, engine='openpyxl')
        
        # Verificar si las columnas necesarias existen
        if 'Log Message' not in df.columns:
            st.error("El archivo no contiene la columna 'Log Message'.")
            return []
        
        return df['Log Message'].tolist()
        
    except Exception as e:
        st.error(f"Error al leer el archivo de Excel: {e}")
        return []

# Función para generar explicaciones detalladas para cada tipo de log
def generar_explicacion(log):
    if "Database connection failed" in log:
        return "Fallo en la conexión con la base de datos."
    elif "Unable to reach API endpoint" in log:
        return "No se pudo comunicar con el endpoint de la API."
    elif "Failed to back up database" in log:
        return "La copia de seguridad de la base de datos falló."
    elif "High memory usage detected" in log:
        return "Uso elevado de memoria detectado."
    elif "Disk space low" in log:
        return "Espacio en disco insuficiente."
    elif "Slow response time" in log:
        return "El tiempo de respuesta del sistema es lento."
    elif "System outage detected" in log:
        return "Se ha detectado una interrupción del sistema."
    elif "Security breach detected" in log:
        return "Posible brecha de seguridad detectada."
    elif "Application crash" in log:
        return "Una aplicación se ha bloqueado inesperadamente."
    elif "User session timeout" in log:
        return "La sesión del usuario ha expirado."
    elif "Unauthorized access attempt" in log:
        return "Intento de acceso no autorizado detectado."
    elif "Server overload" in log:
        return "El servidor está sobrecargado."
    else:
        return "Evento registrado requiere revisión."

# Función para analizar los logs y categorizar los eventos
def analizar_logs(logs):
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for log in logs:
        explicacion = generar_explicacion(log)
        if 'ERROR' in log:
            errores.append((log, explicacion))
        elif 'WARNING' in log:
            advertencias.append((log, explicacion))
        elif 'CRITICAL' in log:
            eventos_criticos.append((log, explicacion))
        else:
            otros_eventos.append((log, explicacion))
    
    return errores, advertencias, eventos_criticos, otros_eventos

# Función para generar un resumen estadístico de los logs
def generar_resumen(errores, advertencias, eventos_criticos, otros_eventos):
    return {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Función para generar el informe de auditoría en formato Word
def generar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs):
    doc = Document()
    
    # Carátula
    doc.add_heading('INFORME DE AUDITORÍA DE LOGS DEL SISTEMA', 0)
    doc.add_paragraph(f'Fecha de Generación: {resumen["Fecha del resumen"]}', style='Heading 3')
    doc.add_paragraph(f'Total de Logs Analizados: {total_logs}', style='Heading 3')
    doc.add_paragraph("\n")
    
    # Introducción y Objetivo
    doc.add_heading('Introducción', level=1)
    doc.add_paragraph(
        "Los logs son registros detallados de eventos que ocurren dentro de un sistema. Estos registros son fundamentales para la monitorización, "
        "diagnóstico y auditoría del sistema, proporcionando un rastro de actividades que permite a los administradores y desarrolladores "
        "identificar y resolver problemas, asegurar el cumplimiento normativo y mantener la seguridad del sistema."
    )
    
    doc.add_heading('Objetivo de la Auditoría', level=1)
    doc.add_paragraph(
        "El objetivo de esta auditoría es evaluar el estado actual del sistema mediante el análisis de los logs generados, identificar patrones de "
        "comportamiento anómalo, y determinar las áreas que requieren atención para mejorar la estabilidad, rendimiento y seguridad del sistema."
    )
    doc.add_paragraph("\n")
    
    # Resumen Ejecutivo
    doc.add_heading('Resumen Ejecutivo', level=1)
    doc.add_paragraph(
        f"Se analizaron un total de {total_logs} logs, de los cuales {resumen['Errores']} fueron clasificados como errores, "
        f"{resumen['Advertencias']} como advertencias y {resumen['Eventos críticos']} como eventos críticos. "
        "La auditoría identificó varios problemas críticos que requieren atención inmediata."
    )
    doc.add_paragraph("Metodología: Los logs fueron categorizados en errores, advertencias, y eventos críticos mediante la identificación de palabras clave en los registros.")
    
    # Análisis de Errores
    doc.add_heading('Análisis de Errores', level=1)
    doc.add_paragraph("A continuación se detallan los errores más comunes encontrados durante la auditoría:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción del Error'
    table.cell(0, 1).text = 'Explicación'
    for error, explicacion in errores:
        row = table.add_row().cells
        row[0].text = error
        row[1].text = explicacion
    doc.add_paragraph("\n")
    
    # Análisis de Advertencias
    doc.add_heading('Análisis de Advertencias', level=1)
    doc.add_paragraph("A continuación se detallan las advertencias más comunes encontradas durante la auditoría:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción de la Advertencia'
    table.cell(0, 1).text = 'Explicación'
    for advertencia, explicacion in advertencias:
        row = table.add_row().cells
        row[0].text = advertencia
        row[1].text = explicacion
    doc.add_paragraph("\n")
    
    # Análisis de Eventos Críticos
    doc.add_heading('Análisis de Eventos Críticos', level=1)
    doc.add_paragraph("A continuación se detallan los eventos críticos más comunes encontrados durante la auditoría:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción del Evento Crítico'
    table.cell(0, 1).text = 'Explicación'
    for evento, explicacion in eventos_criticos:
        row = table.add_row().cells
        row[0].text = evento
        row[1].text = explicacion
    doc.add_paragraph("\n")
    
    # Firma del Auditor
    doc.add_heading('Firmas', level=1)
    doc.add_paragraph("Firma del Auditor: __________________________")
    doc.add_paragraph("Nombre del Auditor: [Nombre del Auditor]")
    doc.add_paragraph("\n")
    
    # Guardar el documento en un buffer en memoria
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

# Función principal para la ejecución de la aplicación en Streamlit
def main():
    st.title("Auditoría de Logs del Sistema")
    
    st.markdown("""
    ### Descripción
    Esta aplicación permite cargar archivos de logs en formato Excel y realizar una auditoría automática para identificar errores, advertencias, y eventos críticos.
    Los resultados se pueden descargar en un informe detallado de Word.
    
    ### Instrucciones
    1. Seleccione un archivo de logs en formato Excel.
    2. El archivo debe contener una columna llamada 'Log Message' con los mensajes de los logs.
    3. Haga clic en 'Generar Informe Word' para descargar un informe detallado de la auditoría.
    """)
    
    archivo_subido = st.file_uploader("Seleccione un archivo de logs en Excel", type="xlsx")
    
    if archivo_subido:
        logs = leer_logs_excel(archivo_subido)
        
        if logs:
            errores, advertencias, eventos_criticos, otros_eventos = analizar_logs(logs)
            
            resumen = generar_resumen(errores, advertencias, eventos_criticos, otros_eventos)
            
            st.subheader("Resumen de Resultados")
            st.write(f"Total de Logs Analizados: {resumen['Total de logs']}")
            st.write(f"Errores: {resumen['Errores']}")
            st.write(f"Advertencias: {resumen['Advertencias']}")
            st.write(f"Eventos
            st.write(f"Eventos Críticos: {resumen['Eventos críticos']}")
            
            if st.button("Generar Informe Word"):
                buffer = generar_informe_word(resumen, errores, advertencias, eventos_criticos, resumen['Total de logs'])
                st.download_button(
                    label="Descargar Informe Word", 
                    data=buffer, 
                    file_name="informe_auditoria_logs.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

if __name__ == "__main__":
    main()
