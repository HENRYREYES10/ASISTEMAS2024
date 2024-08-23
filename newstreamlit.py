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
        return "Fallo en la conexión con la base de datos. Esto podría deberse a credenciales incorrectas, un problema con la red, o el servicio de base de datos no está disponible."
    elif "Unable to reach API endpoint" in message:
        return "No se pudo comunicar con el endpoint de la API. Verifique la URL del endpoint, la conectividad de red y la disponibilidad del servicio."
    elif "Failed to back up database" in message:
        return "La copia de seguridad falló. Posibles causas incluyen falta de espacio en disco, permisos insuficientes, o problemas con el servicio de respaldo."
    elif "High memory usage detected" in message:
        return "Uso elevado de memoria detectado. Revise los procesos en ejecución, posibles fugas de memoria o configuraciones inadecuadas de aplicaciones."
    elif "Disk space low" in message:
        return "Espacio en disco insuficiente. Se recomienda liberar espacio eliminando archivos innecesarios o ampliar la capacidad de almacenamiento."
    elif "Slow response time" in message:
        return "El sistema responde lentamente. Podría ser debido a alta carga de CPU, cuellos de botella en el acceso a la base de datos, o problemas de red."
    elif "System outage detected" in message:
        return "Interrupción del sistema detectada. Verifique la integridad del hardware, la configuración de la red, y el estado de los servicios críticos."
    elif "Security breach detected" in message:
        return "Posible brecha de seguridad detectada. Revise los logs de acceso, cambie contraseñas comprometidas, y considere fortalecer las medidas de seguridad."
    elif "Application crash" in message:
        return "Una aplicación se bloqueó. Revise los registros de la aplicación para identificar la causa del fallo y considere implementar mecanismos de recuperación."
    elif "User session timeout" in message:
        return "La sesión del usuario expiró. Esto podría deberse a configuraciones de tiempo de espera muy bajas o a inactividad prolongada del usuario."
    elif "Unauthorized access attempt" in message:
        return "Intento de acceso no autorizado detectado. Revise los registros de seguridad para identificar al actor y considere aumentar las medidas de protección."
    elif "Server overload" in message:
        return "El servidor está sobrecargado. Considere optimizar las aplicaciones, balancear la carga o aumentar los recursos del servidor."
    elif "Data synchronization error" in message:
        return "Error en la sincronización de datos. Verifique las conexiones de red, la consistencia de datos y los procesos de sincronización."
    elif "API rate limit exceeded" in message:
        return "Límite de tasa de API excedido. Optimice las llamadas a la API para evitar exceder los límites y considere implementar un manejo de tasas."
    elif "Invalid input detected" in message:
        return "Se ha detectado una entrada inválida. Asegúrese de que los datos introducidos cumplen con los formatos y requisitos esperados."
    elif "Password reset requested" in message:
        return "Solicitud de restablecimiento de contraseña detectada. Verifique si se trata de una solicitud legítima y si es necesario tomar medidas adicionales."
    elif "Failed login attempt detected" in message:
        return "Intento de inicio de sesión fallido detectado. Puede ser indicativo de intentos de acceso no autorizados o errores en la autenticación del usuario."
    elif "Session timeout" in message:
        return "Tiempo de sesión agotado. Los usuarios han sido desconectados por inactividad prolongada o debido a políticas de seguridad."
    elif "Scheduled report generated" in message:
        return "Un informe programado se ha generado correctamente. Revise el contenido para asegurar que los datos presentados son precisos y relevantes."
    elif "Customer record updated" in message:
        return "El registro de un cliente ha sido actualizado. Verifique los cambios para asegurar que se reflejan correctamente en el sistema."
    elif "Data export completed" in message:
        return "Exportación de datos completada. Revise el archivo exportado para confirmar que todos los datos necesarios están presentes y son correctos."
    elif "User logged in successfully" in message:
        return "Inicio de sesión exitoso. El usuario ha accedido al sistema correctamente."
    else:
        return "Este evento registrado requiere una revisión detallada para determinar su impacto y causas exactas."

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

    # Añadir análisis detallado
    doc.add_heading('Análisis de Eventos', level=1)

    # Analizar Errores
    if errores:
        doc.add_heading('Errores', level=2)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.cell(0, 0).text = 'Mensaje del Error'
        table.cell(0, 1).text = 'Hora'
        table.cell(0, 2).text = 'Explicación'
        agregar_bordes_tabla(table)
        
        for log, explicacion in errores:
            row = table.add_row().cells
            row[0].text = str(log[1])
            row[1].text = str(log[2])
            row[2].text = explicacion

    # Analizar Advertencias
    if advertencias:
        doc.add_heading('Advertencias', level=2)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.cell(0, 0).text = 'Mensaje de la Advertencia'
        table.cell(0, 1).text = 'Hora'
        table.cell(0, 2).text = 'Explicación'
        agregar_bordes_tabla(table)
        
        for log, explicacion in advertencias:
            row = table.add_row().cells
            row[0].text = str(log[1])
            row[1].text = str(log[2])
            row[2].text = explicacion

    # Analizar Eventos Críticos
    if eventos_criticos:
        doc.add_heading('Eventos Críticos', level=2)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.cell(0, 0).text = 'Mensaje del Evento Crítico'
        table.cell(0, 1).text = 'Hora'
        table.cell(0, 2).text = 'Explicación'
        agregar_bordes_tabla(table)
        
        for log, explicacion in eventos_criticos:
            row = table.add_row().cells
            row[0].text = str(log[1])
            row[1].text = str(log[2])
            row[2].text = explicacion

    # Analizar Otros Eventos
    if otros_eventos:
        doc.add_heading('Otros Eventos', level=2)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.cell(0, 0).text = 'Mensaje del Evento'
        table.cell(0, 1).text = 'Hora'
        table.cell(0, 2).text = 'Explicación'
        agregar_bordes_tabla(table)
        
        for log, explicacion in otros_eventos:
            row = table.add_row().cells
            row[0].text = str(log[1])
            row[1].text = str(log[2])
            row[2].text = explicacion

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
        
        ### Tipos de Logs Soportados
        Esta herramienta puede analizar y categorizar los siguientes tipos de logs:
        - Conexión fallida a la base de datos
        - Incapacidad para alcanzar endpoints de API
        - Errores de sincronización de datos
        - Intentos de acceso no autorizado
        - Sobrecargas del servidor
        - Y muchos más...
        
        ### Beneficios de la Auditoría de Logs
        Realizar una auditoría de logs proporciona una visión detallada de los eventos del sistema, permitiendo:
        - Identificar y corregir problemas críticos rápidamente.
        - Mejorar la seguridad al detectar intentos de acceso no autorizado.
        - Optimizar el rendimiento del sistema mediante la identificación de cuellos de botella.
        - Asegurar el cumplimiento normativo al mantener un registro detallado de todas las actividades.
        
        ### Instrucciones para Usar la Herramienta
        1. **Seleccione los archivos de logs:** Puede cargar múltiples archivos de logs en formato `.log` o archivos de Excel `.xlsx`.
        2. **Analice los logs:** Los registros serán analizados y categorizados.
        3. **Genere un informe:** Haga clic en el botón para generar un informe de auditoría en formato Word.
        
        ### Descarga e Interpretación del Informe
        Una vez completado el análisis de logs, puede descargar un informe detallado en formato Word. El informe incluye:
        - Un resumen ejecutivo de los resultados.
        - Análisis detallado de errores, advertencias y eventos críticos.
        - Recomendaciones específicas para mejorar la estabilidad y seguridad del sistema.
        
        Para descargar el informe, haga clic en el botón "Generar Informe Word" y luego en "Descargar Informe Word".
        
        ### ¿Necesita Ayuda?
        Si tiene alguna pregunta o necesita asistencia, por favor, [contáctenos](#).
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
