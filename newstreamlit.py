import os
import datetime
from collections import Counter
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import matplotlib.pyplot as plt

defleer_logs(file):
    """Lee y decodifica los logs desde un archivo."""try:
        return file.read().decode('latin-1').splitlines()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []

defgenerar_explicacion(log):
    """Genera una explicación detallada basada en el contenido del log."""if"Database connection failed"in log:
        return"Este error indica un fallo en la conexión con la base de datos. Es crucial verificar las credenciales y el estado del servicio de la base de datos."elif"Unable to reach API endpoint"in log:
        return"Este error sugiere que el sistema no pudo comunicarse con el endpoint de la API. Verifique la conectividad de red y la disponibilidad del servicio."elif"Failed to back up database"in log:
        return"La copia de seguridad de la base de datos falló. Esto podría deberse a problemas de espacio en disco o permisos insuficientes."elif"High memory usage detected"in log:
        return"El sistema ha detectado un uso elevado de memoria. Es recomendable revisar los procesos en ejecución y optimizar el uso de recursos."elif"Disk space low"in log:
        return"El espacio en disco es insuficiente. Se recomienda liberar espacio o aumentar la capacidad del almacenamiento."elif"Slow response time"in log:
        return"El tiempo de respuesta del sistema es lento. Esto podría ser causado por una carga excesiva o cuellos de botella en el sistema."elif"System outage detected"in log:
        return"Se ha detectado una interrupción del sistema. Es posible que haya fallas en el hardware o problemas de red que requieran atención inmediata."elif"Security breach detected"in log:
        return"Se ha detectado una posible brecha de seguridad. Revise los accesos y tome medidas correctivas para proteger el sistema."elif"Application crash"in log:
        return"Una aplicación se ha bloqueado inesperadamente. Es necesario revisar los registros de la aplicación para identificar la causa del fallo."elif"User session timeout"in log:
        return"La sesión del usuario ha expirado. Esto podría deberse a inactividad prolongada o a un problema en la configuración del tiempo de espera."elif"Unauthorized access attempt"in log:
        return"Se detectó un intento de acceso no autorizado. Se recomienda revisar los registros de seguridad y tomar medidas para fortalecer la protección."elif"Server overload"in log:
        return"El servidor está sobrecargado. Es necesario distribuir la carga de trabajo o aumentar la capacidad del servidor."else:
        return"Este evento registrado requiere una revisión detallada."defanalizar_logs(logs):
    """Clasifica los logs en errores, advertencias, eventos críticos y otros eventos."""
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for log in logs:
        explicacion = generar_explicacion(log)
        if'ERROR'in log:
            errores.append((log, explicacion))
        elif'WARNING'in log:
            advertencias.append((log, explicacion))
        elif'CRITICAL'in log:
            eventos_criticos.append((log, explicacion))
        else:
            otros_eventos.append((log, explicacion))
    
    return errores, advertencias, eventos_criticos, otros_eventos

defcombinar_resultados(resultados):
    """Combina los resultados de análisis de múltiples archivos de logs."""
    errores, advertencias, eventos_criticos, otros_eventos = [], [], [], []
    
    for resultado in resultados:
        errores.extend(resultado[0])
        advertencias.extend(resultado[1])
        eventos_criticos.extend(resultado[2])
        otros_eventos.extend(resultado[3])
    
    return errores, advertencias, eventos_criticos, otros_eventos

defgenerar_resumen(errores, advertencias, eventos_criticos, otros_eventos):
    """Genera un resumen estadístico de los logs."""defobtener_ultima_palabra(log):
        ifisinstance(log, str):
            partes = log.split(' ')
            return partes[-1] iflen(partes) > 1else"Desconocido"return"Desconocido"return {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Errores más comunes': Counter([obtener_ultima_palabra(log[0]) for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([obtener_ultima_palabra(log[0]) for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([obtener_ultima_palabra(log[0]) for log in eventos_criticos]).most_common(5),
        'Frecuencia de errores por hora': Counter([log[0].split(' ')[1] for log in errores ifisinstance(log[0], str) andlen(log[0].split(' ')) > 1]),
        'Frecuencia de advertencias por hora': Counter([log[0].split(' ')[1] for log in advertencias ifisinstance(log[0], str) andlen(log[0].split(' ')) > 1]),
        'Frecuencia de eventos críticos por hora': Counter([log[0].split(' ')[1] for log in eventos_criticos ifisinstance(log[0], str) andlen(log[0].split(' ')) > 1]),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

defagregar_bordes_tabla(tabla):
    """Añade bordes a todas las celdas de una tabla en un documento de Word."""
    tbl = tabla._tbl  # Obtener la tabla OXMLfor cell in tbl.iter_tcs():
        tcPr = cell.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')  # Tamaño del borde
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), '000000')  # Color del borde (negro)
            tcBorders.append(border)
        tcPr.append(tcBorders)

defgenerar_grafico_frecuencia(frecuencia, titulo):
    """Genera un gráfico de barras basado en la frecuencia de eventos."""
    horas = sorted(frecuencia.keys())
    valores = [frecuencia[hora] for hora in horas]
    
    plt.figure(figsize=(10, 6))
    plt.bar(horas, valores, color='skyblue')
    plt.xlabel('Hora')
    plt.ylabel('Frecuencia')
    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

defgenerar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs, nombre_auditor):
    """Genera un informe de auditoría en formato Word."""
    doc = Document()
    
    # Portada
    doc.add_heading("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", level=1)
    doc.add_paragraph(f"Fecha de Generación: {resumen['Fecha del resumen']}")
    doc.add_paragraph(f"Total de Logs Analizados: {total_logs}")
    doc.add_paragraph("\n")
    
    # Datos del Auditor
    doc.add_heading("Datos del Auditor", level=2)
    doc.add_paragraph(f"Nombre del Auditor: {nombre_auditor}")
    doc.add_paragraph("Cargo: Auditor de Sistemas")
    doc.add_paragraph("Fecha del Informe: " + resumen['Fecha del resumen'])
    doc.add_paragraph("\n")
    
    # Introducción y Objetivo
    doc.add_heading("Introducción", level=2)
    doc.add_paragraph(
        "Los logs son registros detallados de eventos que ocurren dentro de un sistema. ""Estos registros son fundamentales para la monitorización, diagnóstico y auditoría ""del sistema, proporcionando un rastro de actividades que permite a los administradores ""y desarrolladores identificar y resolver problemas, asegurar el cumplimiento normativo y ""mantener la seguridad del sistema. Este informe tiene como objetivo analizar los logs ""proporcionados, identificar posibles errores, advertencias y eventos críticos, y ofrecer ""recomendaciones basadas en los hallazgos."
    )
    
    doc.add_heading("Objetivo de la Prueba", level=2)
    doc.add_paragraph(
        "El objetivo de esta auditoría es evaluar el estado actual del sistema mediante el análisis ""de los logs generados, identificar patrones de comportamiento anómalo, y determinar las áreas ""que requieren atención para mejorar la estabilidad, rendimiento y seguridad del sistema."
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
    doc.add_paragraph("9. Firmas")
    doc.add_paragraph("\n")
    
    # Resumen Ejecutivo
    doc.add_heading("1. Resumen Ejecutivo", level=2)
    doc.add_paragraph(f"Se analizaron un total de {total_logs} logs, de los cuales {resumen['Errores']} "f"fueron clasificados como errores, {resumen['Advertencias']} como advertencias y "f"{resumen['Eventos críticos']} como eventos críticos. La auditoría identificó "f"varios problemas críticos que requieren atención inmediata.")
    doc.add_paragraph("Metodología: Los logs fueron categorizados en errores, advertencias, y eventos críticos ""mediante la identificación de palabras clave en los registros. Se generaron resúmenes ""estadísticos y gráficos para visualizar la distribución de los problemas detectados.")
    doc.add_paragraph("\n")
    
    # Análisis de Errores
    doc.add_heading("2. Análisis de Errores", level=2)
    doc.add_paragraph("A continuación se detallan los errores más comunes encontrados:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Descripción del Error'
    table.cell(0, 1).text = 'Ocurrencias'
    agregar_bordes_tabla(table)
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
    agregar_bordes_tabla(table)
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
    agregar_bordes_tabla(table)
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
    agregar_bordes_tabla(table)
    for hora, frecuencia insorted(resumen['Frecuencia de errores por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    
    doc.add_paragraph("Frecuencia de Advertencias por Hora:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Hora'
    table.cell(0, 1).text = 'Advertencias'
    agregar_bordes_tabla(table)
    for hora, frecuencia insorted(resumen['Frecuencia de advertencias por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    
    doc.add_paragraph("Frecuencia de Eventos Críticos por Hora:")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Hora'
    table.cell(0, 1).text = 'Eventos Críticos'
    agregar_bordes_tabla(table)
    for hora, frecuencia insorted(resumen['Frecuencia de eventos críticos por hora'].items()):
        row = table.add_row().cells
        row[0].text = f"{hora}:00"
        row[1].text = str(frecuencia)
    doc.add_paragraph("\n")

    # Incluir gráficos en el informe
    doc.add_heading("Gráficos de Distribución Temporal", level=2)
    for titulo, frecuencia in [
        ("Frecuencia de Errores por Hora", resumen['Frecuencia de errores por hora']),
        ("Frecuencia de Advertencias por Hora", resumen['Frecuencia de advertencias por hora']),
        ("Frecuencia de Eventos Críticos por Hora", resumen['Frecuencia de eventos críticos por hora'])
    ]:
        grafico = generar_grafico_frecuencia(frecuencia, titulo)
        doc.add_paragraph(titulo)
        doc.add_picture(grafico, width=Pt(480))

    # Patrones Recurrentes
    doc.add_heading("6. Patrones Recurrentes", level=2)
    doc.add_paragraph("En esta sección se identifican patrones recurrentes de errores y advertencias a lo largo del tiempo.")
    
    # Detalles Específicos
    doc.add_heading("7. Detalles de Errores, Advertencias y Eventos Críticos", level=2)
    
    doc.add_heading("Errores:", level=3)
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Log'
    table.cell(0, 1).text = 'Explicación'
    agregar_bordes_tabla(table)
    for log, explicacion in errores:
        row = table.add_row().cells
        row[0].text = log
        row[1].text = explicacion
    
    doc.add_heading("Advertencias:", level=3)
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Log'
    table.cell(0, 1).text = 'Explicación'
    agregar_bordes_tabla(table)
    for log, explicacion in advertencias:
        row = table.add_row().cells
        row[0].text = log
        row[1].text = explicacion
    
    doc.add_heading("Eventos Críticos:", level=3)
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = 'Log'
    table.cell(0, 1).text = 'Explicación'
    agregar_bordes_tabla(table)
    for log, explicacion in eventos_criticos:
        row = table.add_row().cells
        row[0].text = log
        row[1].text = explicacion
    doc.add_paragraph("\n")
    
    # Conclusiones y Recomendaciones
    doc.add_heading("8. Conclusiones y Recomendaciones", level=2)
    doc.add_paragraph(
        "A partir del análisis de los logs, se identificaron varios problemas críticos que requieren atención inmediata. ""Es fundamental implementar medidas correctivas para evitar que los errores detectados afecten la estabilidad y seguridad del sistema. ""Se recomienda una revisión exhaustiva de los componentes del sistema implicados en los errores más comunes, así como la implementación de mejores prácticas ""para la monitorización y el mantenimiento preventivo."
    )
    
    # Firma del Auditor
    doc.add_heading("9. Firmas", level=2)
    doc.add_paragraph("Firma del Auditor: __________________________")
    doc.add_paragraph(f"Nombre del Auditor: {nombre_auditor}")
    doc.add_paragraph("\n")
    
    # Guardar el documento en un buffer en memoria
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

defmain():
    st.title("Auditoría de Logs del Sistema")
    
    # Entrada del nombre del auditor
    nombre_auditor = st.text_input("Ingrese su nombre")
    
    archivos_subidos = st.file_uploader("Seleccione los archivos de logs", accept_multiple_files=True, type="log")
    
    if archivos_subidos and nombre_auditor:
        resultados = []
        total_logs = 0for archivo in archivos_subidos:
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
            buffer = generar_informe_word(resumen, errores, advertencias, eventos_criticos, total_logs, nombre_auditor)
            st.download_button(label="Descargar Informe Word", data=buffer, file_name="informe_auditoria_logs.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
