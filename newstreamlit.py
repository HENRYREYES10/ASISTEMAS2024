import pandas as pd
import streamlit as st
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import datetime
from collections import Counter

# Función para leer los logs desde un archivo de texto
def leer_logs(file):
    try:
        return file.read().decode('latin-1').splitlines()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []

# Función para leer los logs desde un archivo de Excel
def leer_logs_excel(file):
    try:
        df = pd.read_excel(file, engine='openpyxl')
        st.write("Columnas disponibles en la hoja seleccionada:", df.columns)
        
        # Verifica que la columna 'Log Message' exista
        if 'Log Message' not in df.columns:
            st.error("La columna 'Log Message' no se encuentra en la hoja seleccionada.")
            return []
        
        return df['Log Message'].tolist()
        
    except Exception as e:
        st.error(f"Error al leer el archivo de Excel: {e}")
        return []

# Función para generar explicaciones detalladas para cada tipo de log
def generar_explicacion(log):
    # (Aquí irían las explicaciones de cada tipo de log, como en tu código original)
    return "Este evento registrado requiere una revisión detallada."

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

# Función para combinar resultados de múltiples archivos de logs
def combinar_resultados(resultados):
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for resultado in resultados:
        errores.extend(resultado[0])
        advertencias.extend(resultado[1])
        eventos_criticos.extend(resultado[2])
        otros_eventos.extend(resultado[3])
    
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
    
    # Resto del contenido del informe
    # (Aquí irían las secciones del informe como en tu código original)
    
    # Guardar el documento en un buffer en memoria
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

# Función principal para la ejecución de la aplicación en Streamlit
def main():
    st.title("Auditoría de Logs del Sistema")
    archivos_subidos = st.file_uploader("Seleccione los archivos de logs", accept_multiple_files=True, type=["log", "xlsx"])
    
    if archivos_subidos:
        resultados = []
        total_logs = 0
        
        for archivo in archivos_subidos:
            if archivo.name.endswith('.xlsx'):
                logs = leer_logs_excel(archivo)
            else:
                logs = leer_logs(archivo)
            
            total_logs += len(logs)
            if logs:
                resultados.append(analizar_logs(logs))
        
        errores, advertencias, eventos_criticos, otros_eventos = combinar_resultados(resultados)
        
        resumen = generar_resumen(errores, advertencias, eventos_criticos, otros_eventos)
        
        st.subheader("Resumen de Resultados")
        st.write(f"Total de Logs Analizados: {total_logs}")
        st.write(f"Errores: {resumen['Errores']}")
        st.write(f"Advertencias: {resumen['Advertencias']}")
        st.write(f"Eventos Críticos: {resumen['Eventos críticos']}")
        
        if st.button("Generar Informe Word"):
            buffer = generar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs)
            st.download_button(label="Descargar Informe Word", data=buffer, file_name="informe_auditoria_logs.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
