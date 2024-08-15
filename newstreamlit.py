import os
import datetime
from collections import Counter
import streamlit as st
from docx import Document
from io import BytesIO

def leer_logs(file):
    try:
        return file.read().decode('latin-1').splitlines()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []

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

def combinar_resultados(resultados):
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for resultado in resultados:
        errores.extend(resultado[0])
        advertencias.extend(resultado[1])
        eventos_criticos.extend(resultado[2])
        otros_eventos.extend(resultado[3])
    
    return errores, advertencias, eventos_criticos, otros_eventos

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

def generar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs):
    doc = Document()
    
    # Portada
    doc.add_heading("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", level=1)
    doc.add_paragraph(f"Fecha de Generación: {resumen['Fecha del resumen']}")
    doc.add_paragraph(f"Total de Logs Analizados: {total_logs}")
    doc.add_paragraph("\n")
    
    # Introducción y Objetivo
    doc.add_heading("Introducción", level=2)
    doc.add_paragraph(
        "Los logs son registros detallados de eventos que ocurren dentro de un sistema. "
        "Estos registros son fundamentales para la monitorización, diagnóstico y auditoría "
        "del sistema, proporcionando un rastro de actividades que permite a los administradores "
        "y desarrolladores identificar y resolver problemas, asegurar el cumplimiento normativo y "
        "mantener la seguridad del sistema. Este informe tiene como objetivo analizar los logs "
        "proporcionados, identificar posibles errores, advertencias y eventos críticos, y ofrecer "
        "recomendaciones basadas en los hallazgos."
    )
    
    doc.add_heading("Objetivo de la Prueba", level=2)
    doc.add_paragraph(
        "El objetivo de esta auditoría es evaluar el estado actual del sistema mediante el análisis "
        "de los logs generados, identificar patrones de comportamiento anómalo, y determinar las áreas "
        "que requieren atención para mejorar la estabilidad, rendimiento y seguridad del sistema."
    )
    doc.add_paragraph("\n")
    
    # Índice
    doc.add_heading("Índice", level=2)
    doc.add_paragraph("1. Resumen Ejecutivo")
    doc.add_paragraph("2. Análisis de Errores")
    doc.add_paragraph("3. Análisis de Advertencias")
    doc.add_paragraph("4. Análisis de Eventos Críticos")
    doc.add_paragraph("5. Distribución Temporal de Eventos")
    doc.add_paragraph("6. Patrones Recurrentes")
    doc.add_paragraph("7. Detalles de Errores, Advertencias y Eventos Críticos")
    doc.add_paragraph("8. Conclusiones y Recomendaciones")
    doc.add_paragraph("\n")
    
    # Resumen Ejecutivo
    doc.add_heading("1. Resumen Ejecutivo", level=2)
    doc.add_paragraph(f"Se analizaron un total de {total_logs} logs, de los cuales {resumen['Errores']} "
                      f"fueron clasificados como errores, {resumen['Advertencias']} como advertencias y "
                      f"{resumen['Eventos críticos']} como eventos críticos. La auditoría identificó "
                      f"varios problemas críticos que requieren atención inmediata.")
    doc.add_paragraph("Metodología: Los logs fueron categorizados en errores, advertencias, y eventos críticos "
                      "mediante la identificación de palabras clave en los registros. Se generaron resúmenes "
                      "estadísticos y gráficos para visualizar la distribución de los problemas detectados.")
    doc.add_paragraph("\n")
    
    # Análisis de Errores
    doc.add_heading("2. Análisis de Errores", level=2)
    doc.add_paragraph("A continuación se detallan los errores más comunes encontrados:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción del Error'
    table.cell(0, 1).text = 'Ocurrencias'
    for error, ocurrencias in resumen['Errores más comunes']:
        row = table.add_row().cells
        row[0].text = error
        row[1].text = str(ocurrencias)
    doc.add_paragraph("\n")
    
    # Análisis de Advertencias
    doc.add_heading("3. Análisis de Advertencias", level=2)
    doc.add_paragraph("A continuación se detallan las advertencias más comunes encontradas:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción de la Advertencia'
    table.cell(0, 1).text = 'Ocurrencias'
    for advertencia, ocurrencias in resumen['Advertencias más comunes']:
        row = table.add_row().cells
        row[0].text = advertencia
        row[1].text = str(ocurrencias)
    doc.add_paragraph("\n")
    
    # Análisis de Eventos Críticos
    doc.add_heading("4. Análisis de Eventos Críticos", level=2)
    doc.add_paragraph("A continuación se detallan los eventos críticos más comunes encontrados:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción del Evento Crítico'
    table.cell(0, 1).text = 'Ocurrencias'
    for evento, ocurrencias in resumen['Eventos críticos más comunes']:
        row = table.add_row().cells
        row[0].text = evento
        row[1].text = str(ocurrencias)
    doc.add_paragraph("\n")
    
    # Distribución Temporal de Eventos
    doc.add_heading("5. Distribución Temporal de Eventos", level=2)
    doc.add_paragraph("Frecuencia de Errores por Hora:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Hora'
    table.cell(0, 1).text = 'Errores'
    for hora, frecuencia in sorted(resumen['Frecuencia de errores por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    
    doc.add_paragraph("Frecuencia de Advertencias por Hora:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Hora'
    table.cell(0, 1).text = 'Advertencias'
    for hora, frecuencia in sorted(resumen['Frecuencia de advertencias por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    
    doc.add_paragraph("Frecuencia de Eventos Críticos por Hora:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Hora'
    table.cell(0, 1).text = 'Eventos Críticos'
    for hora, frecuencia in sorted(resumen['Frecuencia de eventos críticos por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    doc.add_paragraph("\n")
    
    # Patrones Recurrentes
    doc.add_heading("6. Patrones Recurrentes", level=2)
    doc.add_paragraph("En esta sección se identifican patrones recurrentes de errores y advertencias a lo largo del tiempo.")
    
    # Detalles Específicos
    doc.add_heading("7. Detalles de Errores, Advertencias y Eventos Críticos", level=2)
    
    doc.add_heading("Errores:", level=3)
    for log, explicacion in errores:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")
    
    doc.add_heading("Advertencias:", level=3)
    for log, explicacion in advertencias:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")
    
    doc.add_heading("Eventos Críticos:", level=3)
    for log, explicacion in eventos_criticos:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")
    doc.add_paragraph("\n")
    
    # Conclusiones y Recomendaciones
    doc.add_heading("8. Conclusiones y Recomendaciones", level=2)
    doc.add_paragraph(
        "A partir del análisis de los logs, se identificaron varios problemas críticos que requieren atención inmediata. "
        "Es fundamental implementar medidas correctivas para evitar que los errores detectados afecten la estabilidad y seguridad del sistema. "
        "Se recomienda una revisión exhaustiva de los componentes del sistema implicados en los errores más comunes, así como la implementación de mejores prácticas "
        "para la monitorización y el mantenimiento preventivo."
    )
    
    # Guardar el documento en un buffer en memoria
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

# Función principal para la ejecución de la aplicación en Streamlit
def main():
    st.title("Auditoría de Logs del Sistema")
    archivos_subidos = st.file_uploader("Seleccione los archivos de logs", accept_multiple_files=True, type="log")
    
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
            buffer = generar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs)
            st.download_button(label="Descargar Informe Word", data=buffer, file_name="informe_auditoria_logs.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
