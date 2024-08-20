import os
import datetime
from collections import Counter
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO

def leer_logs(file):
    """Lee y decodifica los logs desde un archivo subido."""
    try:
        return file.read().decode('latin-1').splitlines()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return []

def generar_explicacion(log):
    """Genera una explicación detallada basada en el contenido del log."""
    explicaciones = {
        "Database connection failed": "Este error indica un fallo en la conexión con la base de datos. Es crucial verificar las credenciales y el estado del servicio de la base de datos.",
        "Unable to reach API endpoint": "Este error sugiere que el sistema no pudo comunicarse con el endpoint de la API. Verifique la conectividad de red y la disponibilidad del servicio.",
        "Failed to back up database": "La copia de seguridad de la base de datos falló. Esto podría deberse a problemas de espacio en disco o permisos insuficientes.",
        "High memory usage detected": "El sistema ha detectado un uso elevado de memoria. Es recomendable revisar los procesos en ejecución y optimizar el uso de recursos.",
        "Disk space low": "El espacio en disco es insuficiente. Se recomienda liberar espacio o aumentar la capacidad del almacenamiento.",
        "Slow response time": "El tiempo de respuesta del sistema es lento. Esto podría ser causado por una carga excesiva o cuellos de botella en el sistema.",
        "System outage detected": "Se ha detectado una interrupción del sistema. Es posible que haya fallas en el hardware o problemas de red que requieran atención inmediata.",
        "Security breach detected": "Se ha detectado una posible brecha de seguridad. Revise los accesos y tome medidas correctivas para proteger el sistema.",
        "Application crash": "Una aplicación se ha bloqueado inesperadamente. Es necesario revisar los registros de la aplicación para identificar la causa del fallo.",
        "User session timeout": "La sesión del usuario ha expirado. Esto podría deberse a inactividad prolongada o a un problema en la configuración del tiempo de espera.",
        "Unauthorized access attempt": "Se detectó un intento de acceso no autorizado. Se recomienda revisar los registros de seguridad y tomar medidas para fortalecer la protección.",
        "Server overload": "El servidor está sobrecargado. Es necesario distribuir la carga de trabajo o aumentar la capacidad del servidor."
    }

    for clave, explicacion in explicaciones.items():
        if clave in log:
            return explicacion
    return "Este evento registrado requiere una revisión detallada."

def analizar_logs(logs):
    """Clasifica los logs en errores, advertencias, eventos críticos y otros eventos."""
    categorias = {
        'ERROR': [],
        'WARNING': [],
        'CRITICAL': [],
        'OTROS': []
    }

    for log in logs:
        explicacion = generar_explicacion(log)
        if 'ERROR' in log:
            categorias['ERROR'].append((log, explicacion))
        elif 'WARNING' in log:
            categorias['WARNING'].append((log, explicacion))
        elif 'CRITICAL' in log:
            categorias['CRITICAL'].append((log, explicacion))
        else:
            categorias['OTROS'].append((log, explicacion))
    
    return categorias

def combinar_resultados(resultados):
    """Combina los resultados de análisis de múltiples archivos de logs."""
    combinados = {'ERROR': [], 'WARNING': [], 'CRITICAL': [], 'OTROS': []}
    
    for resultado en resultados:
        for clave en combinados:
            combinados[clave].extend(resultado[clave])
    
    return combinados

def generar_resumen(categorias):
    """Genera un resumen estadístico de los logs."""
    def obtener_ultima_palabra(log):
        partes = log.split(' ')
        return partes[-1] if len(partes) > 1 else "Desconocido"
    
    resumen = {
        'Total de logs': sum(len(categorias[clave]) for clave en categorias),
        'Errores': len(categorias['ERROR']),
        'Advertencias': len(categorias['WARNING']),
        'Eventos críticos': len(categorias['CRITICAL']),
        'Otros eventos': len(categorias['OTROS']),
    }

    for clave en ['ERROR', 'WARNING', 'CRITICAL']:
        resumen[f'{clave.lower()} más comunes'] = Counter(
            obtener_ultima_palabra(log[0]) for log in categorias[clave]
        ).most_common(5)

    resumen['Frecuencia de errores por hora'] = Counter(
        log[0].split(' ')[1] for log in categorias['ERROR'] if len(log[0].split(' ')) > 1
    )
    resumen['Frecuencia de advertencias por hora'] = Counter(
        log[0].split(' ')[1] for log in categorias['WARNING'] if len(log[0].split(' ')) > 1
    )
    resumen['Frecuencia de eventos críticos por hora'] = Counter(
        log[0].split(' ')[1] for log in categorias['CRITICAL'] if len(log[0].split(' ')) > 1
    )

    resumen['Fecha del resumen'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return resumen

def agregar_bordes_tabla(tabla):
    """Añade bordes a todas las celdas de una tabla en un documento de Word."""
    tbl = tabla._tbl  # Obtener la tabla OXML
    for cell in tbl.iter_tcs():
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

def agregar_parrafo_formateado(doc, texto, bold=False, italic=False, font_size=12):
    """Agrega un párrafo formateado al documento de Word."""
    parrafo = doc.add_paragraph()
    run = parrafo.add_run(texto)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(font_size)

def generar_informe_word(resumen, categorias):
    """Genera un informe de auditoría en formato Word."""
    doc = Document()

    # Crear la portada del documento
    doc.add_heading("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", level=1)
    agregar_parrafo_formateado(doc, f"Fecha de Generación: {resumen['Fecha del resumen']}", bold=True)
    agregar_parrafo_formateado(doc, f"Total de Logs Analizados: {resumen['Total de logs']}", bold=True)
    doc.add_paragraph("\n")

    # Añadir datos del auditor
    doc.add_heading("Datos del Auditor", level=2)
    agregar_parrafo_formateado(doc, "Nombre del Auditor: [Nombre del Auditor]", bold=True)
    agregar_parrafo_formateado(doc, "Cargo: Auditor de Sistemas", bold=True)
    agregar_parrafo_formateado(doc, f"Fecha del Informe: {resumen['Fecha del resumen']}", bold=True)
    doc.add_paragraph("\n")

    # Introducción y objetivo de la auditoría
    doc.add_heading("Introducción", level=2)
    agregar_parrafo_formateado(doc,
        "Los logs son registros detallados de eventos que ocurren dentro de un sistema. "
        "Estos registros son fundamentales para la monitorización, diagnóstico y auditoría "
        "del sistema, proporcionando un rastro de actividades que permite a los administradores "
        "y desarrolladores identificar y resolver problemas, asegurar el cumplimiento normativo y "
        "mantener la seguridad del sistema. Este informe tiene como objetivo analizar los logs "
        "proporcionados, identificar posibles errores, advertencias y eventos críticos, y ofrecer "
        "recomendaciones basadas en los hallazgos."
    )

    doc.add_heading("Objetivo de la Prueba", level=2)
    agregar_parrafo_formateado(doc,
        "El objetivo de esta auditoría es evaluar el estado actual del sistema mediante el análisis "
        "de los logs generados, identificar patrones de comportamiento anómalo, y determinar las áreas "
        "que requieren atención para mejorar la estabilidad, rendimiento y seguridad del sistema."
    )
    doc.add_paragraph("\n")

    # Añadir índice
    doc.add_heading("Índice", level=2)
    agregar_parrafo_formateado(doc, "1. Resumen Ejecutivo")
    agregar_parrafo_formateado(doc, "2. Análisis de Errores")
    agregar_parrafo_formateado(doc, "3. Análisis de Advertencias")
    agregar_parrafo_formateado(doc, "4. Análisis de Eventos Críticos")
    agregar_parrafo_formateado(doc, "5. Distribución Temporal de Eventos")
    agregar_parrafo_formateado(doc, "6. Patrones Recurrentes")
    agregar_parrafo_formateado(doc, "7. Detalles de Errores, Advertencias y Eventos Críticos")
    agregar_parrafo_formateado(doc, "8. Conclusiones y Recomendaciones")
    agregar_parrafo_formateado(doc, "9. Firmas")
    doc.add_paragraph("\n")

    # Resumen Ejecutivo
    doc.add_heading("1. Resumen Ejecutivo", level=2)
    agregar_parrafo_formateado(doc, 
        f"Se analizaron un total de {resumen['Total de logs']} logs, de los cuales {resumen['Errores']} "
        f"fueron clasificados como errores, {resumen['Advertencias']} como advertencias y "
        f"{resumen['Eventos críticos']} como eventos críticos. La auditoría identificó "
        f"varios problemas críticos que requieren atención inmediata.")
    agregar_parrafo_formateado(doc, 
        "Metodología: Los logs fueron categorizados en errores, advertencias, y eventos críticos "
        "mediante la identificación de palabras clave en los registros. Se generaron resúmenes "
        "estadísticos y gráficos para visualizar la distribución de los problemas detectados.")
    doc.add_paragraph("\n")

    # Análisis Detallado de Errores, Advertencias y Eventos Críticos
    for categoria, nombre in [('ERROR', 'Errores'), ('WARNING', 'Advertencias'), ('CRITICAL', 'Eventos Críticos')]:
        doc.add_heading(f"2. Análisis de {nombre}", level=2)
        agregar_parrafo_formateado(doc, f"A continuación se detallan los {nombre.lower()} más comunes encontrados:")
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = f'Descripción del {nombre[:-1]}'
        table.cell(0, 1).text = 'Ocurrencias'
        agregar_bordes_tabla(table)
        for log, ocurrencias in resumen[f'{categoria.lower()} más comunes']:
            row = table.add_row().cells
            row[0].text = log
            row[1].text = str(ocurrencias)
        doc.add_paragraph("\n")

    # Distribución Temporal de Eventos
    doc.add_heading("5. Distribución Temporal de Eventos", level=2)
    for clave, nombre en [('Frecuencia de errores por hora', 'Errores'), 
                          ('Frecuencia de advertencias por hora', 'Advertencias'), 
                          ('Frecuencia de eventos críticos por hora', 'Eventos Críticos')]:
        agregar_parrafo_formateado(doc, f"Frecuencia de {nombre} por Hora:")
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = 'Hora'
        table.cell(0, 1).text = nombre
        agregar_bordes_tabla(table)
        for hora, frecuencia in sorted(resumen[clave].items()):
            row = table.add_row().cells
            row[0].text = f"{hora}:00"
            row[1].text = str(frecuencia)
        doc.add_paragraph("\n")

    # Patrones Recurrentes
    doc.add_heading("6. Patrones Recurrentes", level=2)
    agregar_parrafo_formateado(doc, 
        "En esta sección se identifican patrones recurrentes de errores y advertencias a lo largo del tiempo. "
        "Estos patrones pueden indicar problemas subyacentes que requieren una atención especial para mejorar la estabilidad "
        "y seguridad del sistema.")
    
    # Detalles Específicos
    doc.add_heading("7. Detalles de Errores, Advertencias y Eventos Críticos", level=2)
    
    for categoria, nombre in [('ERROR', 'Errores'), ('WARNING', 'Advertencias'), ('CRITICAL', 'Eventos Críticos')]:
        doc.add_heading(f"{nombre}:", level=3)
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = 'Log'
        table.cell(0, 1).text = 'Explicación'
        agregar_bordes_tabla(table)
        for log, explicacion in categorias[categoria]:
            row = table.add_row().cells
            row[0].text = log
            row[1].text = explicacion
        doc.add_paragraph("\n")

    # Conclusiones y Recomendaciones
    doc.add_heading("8. Conclusiones y Recomendaciones", level=2)
    agregar_parrafo_formateado(doc, 
        "A partir del análisis de los logs, se identificaron varios problemas críticos que requieren atención inmediata. "
        "Es fundamental implementar medidas correctivas para evitar que los errores detectados afecten la estabilidad y seguridad del sistema. "
        "Se recomienda una revisión exhaustiva de los componentes del sistema implicados en los errores más comunes, así como la implementación de mejores prácticas "
        "para la monitorización y el mantenimiento preventivo."
    )

    # Firma del Auditor
    doc.add_heading("9. Firmas", level=2)
    agregar_parrafo_formateado(doc, "Firma del Auditor: __________________________")
    agregar_parrafo_formateado(doc, "Nombre del Auditor: [Nombre del Auditor]")
    doc.add_paragraph("\n")

    # Guardar el documento en un buffer en memoria
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer

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
        
        categorias = combinar_resultados(resultados)
        resumen = generar_resumen(categorias)
        
        st.subheader("Resumen de Resultados")
        st.write(f"Total de Logs Analizados: {total_logs}")
        st.write(f"Errores: {resumen['Errores']}")
        st.write(f"Advertencias: {resumen['Advertencias']}")
        st.write(f"Eventos Críticos: {resumen['Eventos críticos']}")
        
        if st.button("Generar Informe Word"):
            buffer = generar_informe_word(resumen, categorias)
            st.download_button(label="Descargar Informe Word", data=buffer, file_name="informe_auditoria_logs.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
