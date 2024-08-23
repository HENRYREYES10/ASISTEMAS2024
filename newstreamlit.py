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
            if 'Severity' in df.columns and 'Message' in df.columns and 'Timestamp' in df.columns:
                return df[['Severity', 'Message', 'Timestamp']].values.tolist()
            else:
                st.error("No se encontraron las columnas 'Severity', 'Message' o 'Timestamp' en el archivo.")
                return []
        else:
            st.error("Formato de archivo no soportado. Suba un archivo .log o .xlsx")
            return []
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []
# Función para generar explicaciones detalladas y personalizadas para cada log
def generar_explicacion(log):
    message = log[1]
    if "Database connection failed" in message:
        return "Fallo en la conexión con la base de datos. Verifique las credenciales y el estado del servicio."
    elif "Unable to reach API endpoint" in message:
        return "No se pudo comunicar con el endpoint de la API. Verifique la conectividad y disponibilidad del servicio."
    elif "Failed to back up database" in message:
        return "La copia de seguridad falló. Posibles causas: problemas de espacio en disco o permisos insuficientes."
    elif "High memory usage detected" in message:
        return "Uso elevado de memoria detectado. Revise los procesos y optimice el uso de recursos."
    elif "Disk space low" in message:
        return "Espacio en disco insuficiente. Se recomienda liberar espacio o aumentar la capacidad de almacenamiento."
    elif "Slow response time" in message:
        return "El sistema responde lentamente. Posibles causas: sobrecarga del sistema o cuellos de botella."
    elif "System outage detected" in message:
        return "Interrupción del sistema detectada. Posible fallo de hardware o problemas de red."
    elif "Security breach detected" in message:
        return "Posible brecha de seguridad detectada. Revise los accesos y tome medidas correctivas."
    elif "Application crash" in message:
        return "Una aplicación se bloqueó. Revise los registros para identificar la causa del fallo."
    elif "User session timeout" in message:
        return "La sesión del usuario expiró. Puede deberse a inactividad prolongada o problemas de configuración."
    elif "Unauthorized access attempt" in message:
        return "Intento de acceso no autorizado detectado. Reforzar la seguridad es recomendado."
    elif "Server overload" in message:
        return "Servidor sobrecargado. Distribuya la carga o aumente la capacidad del servidor."
    elif "Data synchronization error" in message:
        return "Error en la sincronización de datos. Verifique la integridad y conexión del sistema."
    elif "API rate limit exceeded" in message:
        return "Límite de tasa de API excedido. Revise las políticas de uso y optimice las llamadas a la API."
    else:
        return "Este evento registrado requiere una revisión detallada."
# Función para analizar los logs y categorizar los eventos
def analizar_logs(logs):
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for log in logs:
        severity = log[0]
        message = log[1]
        explicacion = generar_explicacion(log)
        if severity == 'ERROR':
            errores.append((log, explicacion))
        elif severity == 'WARNING':
            advertencias.append((log, explicacion))
        elif severity == 'CRITICAL':
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
def generar_informe_word(resumen, errores, advertencias, eventos_criticos, otros_eventos, total_logs):
    doc = Document()
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
    # Sección de Análisis de Errores
    doc.add_heading('Análisis de Errores', level=1)
    for log, explicacion in errores:
        doc.add_paragraph(f"Mensaje: {log[1]}", style='List Bullet')
        doc.add_paragraph(f"Hora: {log[2]}", style='List Bullet')
        doc.add_paragraph(f"Explicación: {explicacion}\n", style='List Bullet')

    # Sección de Análisis de Advertencias
    doc.add_heading('Análisis de Advertencias', level=1)
    for log, explicacion in advertencias:
        doc.add_paragraph(f"Mensaje: {log[1]}", style='List Bullet')
        doc.add_paragraph(f"Hora: {log[2]}", style='List Bullet')
        doc.add_paragraph(f"Explicación: {explicacion}\n", style='List Bullet')

    # Sección de Análisis de Eventos Críticos
    doc.add_heading('Análisis de Eventos Críticos', level=1)
    for log, explicacion in eventos_criticos:
        doc.add_paragraph(f"Mensaje: {log[1]}", style='List Bullet')
        doc.add_paragraph(f"Hora: {log[2]}", style='List Bullet')
        doc.add_paragraph(f"Explicación: {explicacion}\n", style='List Bullet')
    # Recomendaciones y Mejores Prácticas
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
        "regulares para identificar y resolver problemas antes de que se conviertan en críticos.\n"
        "5. **Capacitación de Personal:** Asegurar que el personal esté capacitado para responder de manera efectiva a los incidentes y para utilizar "
        "herramientas de monitoreo y diagnóstico."
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
        
        # Aquí se llama a la función combinar_resultados
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
