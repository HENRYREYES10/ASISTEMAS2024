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
            return df['Message'].tolist()  # Ajusta según la columna de tu Excel
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
        'Errores más comunes': Counter([log[0].split(' ')[-1] for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([log[0].split(' ')[-1] for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([log[0].split(' ')[-1] for log in eventos_criticos]).most_common(5),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Función para añadir bordes a una tabla en Word
def agregar_bordes_tabla(tabla):
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

# Función para generar el informe de auditoría en formato Word con validaciones adicionales
def generar_informe_word(resumen, errores, advertencias, eventos_criticos, otros_eventos, total_logs):
    doc = Document()
    doc.add_heading('INFORME DE AUDITORÍA DE LOGS DEL SISTEMA', 0)
    doc.add_paragraph(f'Fecha de Generación: {resumen.get("Fecha del resumen", "No disponible")}', style='Heading 3')
    doc.add_paragraph(f'Total de Logs Analizados: {total_logs}', style='Heading 3')
    doc.add_paragraph("\n")

    # Índice
    doc.add_heading('Índice', level=1)
    doc.add_paragraph('1. Introducción')
    doc.add_paragraph('2. Objetivo de la Auditoría')
    doc.add_paragraph('3. Metodología')
    doc.add_paragraph('4. Resumen Ejecutivo')
    doc.add_paragraph('5. Análisis de Errores')
    doc.add_paragraph('6. Análisis de Advertencias')
    doc.add_paragraph('7. Análisis de Eventos Críticos')
    doc.add_paragraph('8. Patrones Recurrentes y Observaciones')
    doc.add_paragraph('9. Impacto Potencial de los Problemas Identificados')
    doc.add_paragraph('10. Recomendaciones Detalladas')
    doc.add_paragraph('11. Acciones Correctivas Inmediatas')
    doc.add_paragraph('12. Conclusión')
    doc.add_paragraph('13. Firmas')
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

    # Sección de Análisis Mejorada con Validación de Datos
    def agregar_seccion_analisis(doc, titulo, lista_logs):
        doc.add_heading(titulo, level=1)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.cell(0, 0).text = 'Mensaje'
        table.cell(0, 1).text = 'Hora'
        table.cell(0, 2).text = 'Explicación'
        agregar_bordes_tabla(table)
        
        for log, explicacion in lista_logs:
            row = table.add_row().cells
            mensaje = log[1] if len(log) > 1 and log[1] else "Mensaje no disponible"
            hora = log[2] if len(log) > 2 and log[2] else "Hora no disponible"
            explicacion = explicacion if explicacion else "Explicación no disponible"
            row[0].text = str(mensaje)
            row[1].text = str(hora)
            row[2].text = str(explicacion)
    
    agregar_seccion_analisis(doc, 'Análisis de Errores', errores)
    agregar_seccion_analisis(doc, 'Análisis de Advertencias', advertencias)
    agregar_seccion_analisis(doc, 'Análisis de Eventos Críticos', eventos_criticos)

    # Patrones Recurrentes y Observaciones
    doc.add_heading('Patrones Recurrentes y Observaciones', level=1)
    doc.add_paragraph(
        "Se identificaron varios patrones recurrentes en los logs analizados, lo que sugiere posibles áreas problemáticas en el sistema. "
        "Específicamente, se observó que ciertos errores tienden a ocurrir en intervalos de tiempo similares, lo que podría indicar "
        "problemas relacionados con la carga del sistema o con procesos específicos que se ejecutan en esos momentos. "
        "Además, las advertencias relacionadas con la seguridad requieren atención inmediata para evitar posibles brechas de seguridad."
    )

    # Impacto Potencial de los Problemas Identificados
    doc.add_heading('Impacto Potencial de los Problemas Identificados', level=1)
    doc.add_paragraph(
        "Los problemas identificados en esta auditoría podrían tener un impacto significativo en la operación y seguridad del sistema. "
        "Los errores de conectividad y las sobrecargas de recursos pueden llevar a tiempos de inactividad, afectando la disponibilidad del servicio. "
        "Los intentos de acceso no autorizado y las brechas de seguridad podrían comprometer datos sensibles y la integridad del sistema."
    )

    # Recomendaciones Detalladas
    doc.add_heading('Recomendaciones Detalladas', level=1)
    doc.add_paragraph(
        "Para abordar los problemas identificados, se recomiendan las siguientes acciones específicas:\n"
        "1. **Monitoreo Continuo:** Implementar herramientas de monitoreo para detectar y alertar sobre problemas de conectividad y sobrecarga en tiempo real.\n"
        "2. **Fortalecimiento de la Seguridad:** Revisar y actualizar las políticas de seguridad para prevenir accesos no autorizados, incluyendo autenticación de múltiples factores.\n"
        "3. **Optimización de Recursos:** Realizar un análisis de rendimiento para identificar y eliminar cuellos de botella, mejorando así la eficiencia del sistema.\n"
        "4. **Actualización de la Infraestructura:** Considerar la actualización del hardware o la ampliación de la capacidad del servidor para manejar mejor la carga y los picos de tráfico.\n"
        "5. **Capacitación del Personal:** Asegurar que el personal esté capacitado para responder a incidentes de seguridad y para utilizar herramientas de monitoreo y diagnóstico de manera efectiva.\n"
        "6. **Revisión Periódica de Logs:** Establecer un calendario de revisión de logs para identificar problemas emergentes antes de que se conviertan en críticos.\n"
        "7. **Auditorías de Seguridad:** Realizar auditorías de seguridad regulares para identificar vulnerabilidades y asegurar que las políticas de seguridad se estén aplicando correctamente."
    )

    # Acciones Correctivas Inmediatas
    doc.add_heading('Acciones Correctivas Inmediatas', level=1)
    doc.add_paragraph(
        "Basado en los hallazgos de esta auditoría, se recomiendan las siguientes acciones correctivas inmediatas para mitigar los riesgos identificados:\n"
        "1. **Resolver Problemas de Conectividad:** Identificar y solucionar los problemas de conexión a la base de datos para asegurar la disponibilidad continua del servicio.\n"
        "2. **Aumentar la Capacidad de Almacenamiento:** Revisar y expandir la capacidad de almacenamiento para evitar problemas relacionados con el espacio en disco insuficiente.\n"
        "3. **Implementar Monitoreo de Seguridad:** Instalar herramientas de monitoreo que alerten automáticamente sobre intentos de acceso no autorizado y brechas de seguridad.\n"
        "4. **Optimización de Procesos de Backup:** Asegurarse de que los procesos de respaldo de datos estén configurados correctamente y que se realicen regularmente sin fallos.\n"
        "5. **Actualizar Configuraciones de Tiempo de Sesión:** Revisar y ajustar las configuraciones de tiempo de sesión para evitar cierres inesperados de sesión de usuario debido a configuraciones demasiado estrictas."
    )

    # Conclusión
    doc.add_heading('Conclusión', level=1)
    doc.add_paragraph(
        "La auditoría de logs realizada proporciona una visión integral del estado actual del sistema, identificando tanto problemas críticos como áreas de mejora. "
        "Es evidente que existen problemas de conectividad y sobrecarga de recursos que deben ser abordados para asegurar la estabilidad y disponibilidad del sistema. "
        "Asimismo, los intentos de acceso no autorizado resaltan la necesidad de mejorar las medidas de seguridad. Implementar las recomendaciones propuestas ayudará "
        "a mitigar estos riesgos, mejorar la eficiencia y garantizar la integridad y seguridad del sistema a largo plazo."
    )
    doc.add_paragraph(
        "Se recomienda realizar auditorías de logs periódicamente para mantener un control continuo sobre el estado del sistema y responder proactivamente a cualquier "
        "incidencia que pudiera surgir. La adopción de una estrategia de monitoreo continuo y la actualización regular de políticas y procedimientos de seguridad serán clave "
        "para mantener la resiliencia del sistema ante futuros desafíos."
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
