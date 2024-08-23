import os
import datetime
from collections import Counter
import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import pandas as pd

# Función para leer los logs desde el archivo subido
def leer_logs(file):
    try:
        if file.name.endswith('.log'):
            return file.read().decode('latin-1').splitlines()
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
            if 'Severity' in df.columns and 'Message' in df.columns:
                return df[['Severity', 'Message']].values.tolist()
            else:
                st.error("No se encontraron las columnas 'Severity' o 'Message' en el archivo.")
                return []
        else:
            st.error("Formato de archivo no soportado. Suba un archivo .log o .xlsx")
            return []
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []

# Función para generar explicaciones detalladas para cada tipo de log
def generar_explicacion(log):
    if "Database connection failed" in log:
        return "Este error indica un fallo en la conexión con la base de datos. Es crucial verificar las credenciales y el estado del servicio de la base de datos."
    elif "Unable to reach API endpoint" in log:
        return "Este error sugiere que el sistema no pudo comunicarse con el endpoint de la API. Verifique la conectividad de red y la disponibilidad del servicio."
    elif "Failed to back up database" in log:
        return "La copia de seguridad de la base de datos falló. Esto podría deberse a problemas de espacio en disco o permisos insuficientes."
    elif "High memory usage detected" in log:
        return "El sistema ha detectado un uso elevado de memoria. Es recomendable revisar los procesos en ejecución y optimizar el uso de recursos."
    elif "Disk space low" in log:
        return "El espacio en disco es insuficiente. Se recomienda liberar espacio o aumentar la capacidad del almacenamiento."
    elif "Slow response time" in log:
        return "El tiempo de respuesta del sistema es lento. Esto podría ser causado por una carga excesiva o cuellos de botella en el sistema."
    elif "System outage detected" in log:
        return "Se ha detectado una interrupción del sistema. Es posible que haya fallas en el hardware o problemas de red que requieran atención inmediata."
    elif "Security breach detected" in log:
        return "Se ha detectado una posible brecha de seguridad. Revise los accesos y tome medidas correctivas para proteger el sistema."
    elif "Application crash" in log:
        return "Una aplicación se ha bloqueado inesperadamente. Es necesario revisar los registros de la aplicación para identificar la causa del fallo."
    elif "User session timeout" in log:
        return "La sesión del usuario ha expirado. Esto podría deberse a inactividad prolongada o a un problema en la configuración del tiempo de espera."
    elif "Unauthorized access attempt" in log:
        return "Se detectó un intento de acceso no autorizado. Se recomienda revisar los registros de seguridad y tomar medidas para fortalecer la protección."
    elif "Server overload" in log:
        return "El servidor está sobrecargado. Es necesario distribuir la carga de trabajo o aumentar la capacidad del servidor."
    else:
        return "Este evento registrado requiere una revisión detallada."
# Función para analizar los logs y categorizar los eventos
def analizar_logs(logs):
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for log in logs:
        severity = log[0]
        message = log[1]
        explicacion = generar_explicacion(message)
        if severity == 'ERROR':
            errores.append((message, explicacion))
        elif severity == 'WARNING':
            advertencias.append((message, explicacion))
        elif severity == 'CRITICAL':
            eventos_criticos.append((message, explicacion))
        else:
            otros_eventos.append((message, explicacion))
    
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
    def obtener_ultima_palabra(log):
        if isinstance(log, str):
            partes = log.split(' ')
            return partes[-1] if len(partes) > 1 else "Desconocido"
        return "Desconocido"
    
    return {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Errores más comunes': Counter([obtener_ultima_palabra(log[0]) for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([obtener_ultima_palabra(log[0]) for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([obtener_ultima_palabra(log[0]) for log in eventos_criticos]).most_common(5),
        'Frecuencia de errores por hora': Counter([log[0].split(' ')[1] for log in errores if isinstance(log[0], str) and len(log[0].split(' ')) > 1]),
        'Frecuencia de advertencias por hora': Counter([log[0].split(' ')[1] for log in advertencias if isinstance(log[0], str) and len(log[0].split(' ')) > 1]),
        'Frecuencia de eventos críticos por hora': Counter([log[0].split(' ')[1] for log in eventos_criticos if isinstance(log[0], str) and len(log[0].split(' ')) > 1]),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Función para añadir bordes a una tabla en Word
def agregar_bordes_tabla(tabla):
    tbl = tabla._tbl
    for cell in tbl.iter_tcs():
        tcPr = cell.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), '000000')
            tcBorders.append(border)
        tcPr.append(tcBorders)
# Función para generar el informe de auditoría en formato Word
def generar_informe_word(resumen, errores, advertencias, eventos_criticos, otros_eventos, total_logs):
    doc = Document()
    doc.add_heading('INFORME DE AUDITORÍA DE LOGS DEL SISTEMA', 0)
    doc.add_paragraph(f'Fecha de Generación: {resumen["Fecha del resumen"]}', style='Heading 3')
    doc.add_paragraph(f'Total de Logs Analizados: {total_logs}', style='Heading 3')
    doc.add_paragraph("\n")
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

    # Aquí comienzan los análisis específicos
    doc.add_heading('Resumen Ejecutivo', level=1)
    doc.add_paragraph(
        f"Se analizaron un total de {total_logs} logs, de los cuales {resumen['Errores']} fueron clasificados como errores, "
        f"{resumen['Advertencias']} como advertencias y {resumen['Eventos críticos']} como eventos críticos. "
        "La auditoría identificó varios problemas críticos que requieren atención inmediata."
    )
    doc.add_paragraph("Metodología: Los logs fueron categorizados en errores, advertencias, y eventos críticos mediante la identificación de palabras clave en los registros.")
    
    # Sección de Análisis de Errores
    doc.add_heading('Análisis de Errores', level=1)
    doc.add_paragraph("A continuación se detallan los errores encontrados durante la auditoría:")
    for error in errores:
        doc.add_paragraph(f"{error[0]}: {error[1]}", style='List Bullet')

    # Sección de Análisis de Advertencias
    doc.add_heading('Análisis de Advertencias', level=1)
    doc.add_paragraph("A continuación se detallan las advertencias encontradas durante la auditoría:")
    for advertencia in advertencias:
        doc.add_paragraph(f"{advertencia[0]}: {advertencia[1]}", style='List Bullet')

    # Sección de Análisis de Eventos Críticos
    doc.add_heading('Análisis de Eventos Críticos', level=1)
    doc.add_paragraph("A continuación se detallan los eventos críticos encontrados durante la auditoría:")
    for evento_critico in eventos_criticos:
        doc.add_paragraph(f"{evento_critico[0]}: {evento_critico[1]}", style='List Bullet')

    # Observaciones
    doc.add_heading('Patrones Recurrentes y Observaciones', level=1)
    doc.add_paragraph(
        "Se identificaron varios patrones recurrentes en los logs analizados, lo que sugiere posibles áreas problemáticas en el sistema. "
        "Específicamente, se observó que ciertos errores tienden a ocurrir en intervalos de tiempo similares, lo que podría indicar "
        "problemas relacionados con la carga del sistema o con procesos específicos que se ejecutan en esos momentos. "
        "Además, las advertencias relacionadas con la seguridad requieren atención inmediata para evitar posibles brechas de seguridad."
    )

    # Recomendaciones
    doc.add_heading('Recomendaciones y Mejores Prácticas', level=1)
    doc.add_paragraph(
        "En base a los resultados de la auditoría, se sugieren las siguientes recomendaciones para mejorar la estabilidad y seguridad del sistema:\n"
        "1. **Revisión de la Infraestructura:** Evaluar la infraestructura del sistema para identificar posibles cuellos de botella, "
        "especialmente aquellos que podrían estar causando sobrecargas o fallos de conexión a la base de datos.\n"
        "2. **Monitoreo de Seguridad:** Implementar sistemas de monitoreo de seguridad más robustos para detectar intentos de acceso no autorizados "
        "y brechas de seguridad antes de que puedan ser explotadas.\n"
        "3. **Optimización de Recursos:** Revisar y optimizar el uso de los recursos del sistema, incluyendo memoria y espacio en disco, para evitar "
        "futuros problemas relacionados con el rendimiento.\n"
        "4. **Mantenimiento Preventivo:** Establecer un plan de mantenimiento preventivo que incluya revisiones periódicas de logs y auditorías "
        "regulares para identificar y resolver problemas antes de que se conviertan en críticos."
    )

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
    st.write(
        """
        ### Descripción de la Auditoría de Logs
        Los logs son registros que documentan eventos importantes que ocurren en un sistema de software. Estos registros pueden ayudar a los administradores a diagnosticar problemas, monitorear la seguridad, y asegurar que el sistema esté funcionando correctamente. 
        
        Esta herramienta permite cargar archivos de logs de un sistema, analizar los registros en busca de errores, advertencias, y eventos críticos, y generar un informe detallado en formato Word.
        
        ### Instrucciones para Usar la Herramienta
        1. **Seleccione los archivos de logs:** Puede cargar múltiples archivos de logs en formato `.log` o archivos de Excel `.xlsx`.
        2. **Analice los logs:** Los registros serán analizados y categorizados.
        3. **Genere un informe:** Haga clic en el botón para generar un informe de auditoría en formato Word.
        """
    )
    
    archivos_subidos = st.file_uploader("Seleccione los archivos de logs", accept_multiple_files=True, type=["log", "xlsx"])
    
    if archivos_subidos:
        resultados = []
        total_logs = 0
        
        for archivo in archivos_subidos:
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
            buffer = generar_informe_word(resumen, errores, advertencias, eventos_criticos, otros_eventos, total_logs)
            st.download_button(label="Descargar Informe Word", data=buffer, file_name="informe_auditoria_logs.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
