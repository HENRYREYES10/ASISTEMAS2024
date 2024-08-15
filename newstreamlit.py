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
        return "Fallo en la conexión con la base de datos, lo que podría indicar un problema con el servidor o las credenciales."
    elif "Unable to reach API endpoint" in log:
        return "La aplicación no pudo comunicarse con el endpoint de la API. Esto podría deberse a un problema de red o a que el servicio de la API no está disponible."
    elif "Failed to back up database" in log:
        return "No se pudo realizar la copia de seguridad de la base de datos. Verifique el espacio disponible en el disco y los permisos de acceso."
    elif "High memory usage detected" in log:
        return "El uso de memoria del sistema es elevado, lo que podría llevar a un rendimiento degradado o a fallos del sistema si no se gestiona adecuadamente."
    elif "Disk space low" in log:
        return "El espacio en disco es bajo. Es necesario liberar espacio o aumentar la capacidad del almacenamiento para evitar interrupciones en el servicio."
    elif "Slow response time" in log:
        return "El tiempo de respuesta del sistema es lento, lo que podría afectar la experiencia del usuario y señalar un problema de rendimiento."
    elif "System outage detected" in log:
        return "Se detectó una interrupción en el sistema, lo que podría deberse a un fallo de hardware, una sobrecarga del sistema o un problema de red."
    elif "Security breach detected" in log:
        return "Se detectó una posible brecha de seguridad. Es crucial investigar el incidente para determinar el alcance y mitigar cualquier riesgo."
    elif "Application crash" in log:
        return "La aplicación se bloqueó inesperadamente. Revise los registros de la aplicación para identificar la causa del problema y tomar medidas correctivas."
    elif "User session timeout" in log:
        return "La sesión del usuario expiró, posiblemente debido a inactividad o a un problema en la configuración del tiempo de espera."
    elif "Unauthorized access attempt" in log:
        return "Se detectó un intento de acceso no autorizado, lo que podría indicar un intento de intrusión. Revise los registros de seguridad para más detalles."
    elif "Server overload" in log:
        return "El servidor está sobrecargado, lo que podría llevar a una degradación del rendimiento o a caídas del servicio. Considere equilibrar la carga o aumentar la capacidad del servidor."
    elif "Backup disk full" in log:
        return "El disco de respaldo está lleno, lo que impide realizar nuevas copias de seguridad. Es necesario liberar espacio o utilizar un disco con mayor capacidad."
    elif "Service unavailable" in log:
        return "El servicio no está disponible, lo que podría indicar un problema con el servidor o una interrupción en la red."
    elif "High number of failed login attempts" in log:
        return "Se detectó un número elevado de intentos fallidos de inicio de sesión, lo que podría indicar un intento de fuerza bruta. Se recomienda aumentar las medidas de seguridad."
    elif "System clock synchronization failed" in log:
        return "La sincronización del reloj del sistema falló, lo que podría causar problemas con los registros de eventos y la coherencia de los datos."
    elif "Resource usage exceeded limits" in log:
        return "El uso de recursos ha excedido los límites establecidos, lo que podría llevar a un rendimiento degradado o a fallos del sistema si no se gestiona adecuadamente."
    elif "Security certificate expired" in log:
        return "El certificado de seguridad ha expirado, lo que podría comprometer la seguridad de las comunicaciones en el sistema. Es crucial renovar el certificado a la brevedad."
    elif "Application error" in log:
        return "Ocurrió un error en la aplicación, lo que podría afectar su funcionamiento. Revise los detalles del error y aplique las correcciones necesarias."
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
    
    # Datos del Auditor
    doc.add_heading("Datos del Auditor", level=2)
    doc.add_paragraph("Nombre del Auditor: [Nombre del Auditor]")
    doc.add_paragraph("Cargo: Auditor de Sistemas")
    doc.add_paragraph("Fecha del Informe: " + resumen['Fecha del resumen'])
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
    doc.add_paragraph("2. Alcance y Objetivo de la Auditoría")
    doc.add_paragraph("3. Metodología")
    doc.add_paragraph("4. Análisis de Logs")
    doc.add_paragraph("5. Patrones Recurrentes")
    doc.add_paragraph("6. Conclusiones")
    doc.add_paragraph("7. Recomendaciones")
    doc.add_paragraph("8. Firmas")
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
    
    # Análisis de Logs
    doc.add_heading("4. Análisis de Logs", level=2)
    doc.add_heading("Sección 4.1: Análisis de Errores", level=3)
    doc.add_paragraph("A continuación se detallan los errores encontrados durante el análisis:")
    for error, explicacion in errores:
        doc.add_paragraph(f"Log: {error}")
        doc.add_paragraph(f"Explicación: {explicacion}")
        doc.add_paragraph("\n")
    
    doc.add_heading("Sección 4.2: Análisis de Advertencias", level=3)
    doc.add_paragraph("A continuación se detallan las advertencias encontradas durante el análisis:")
    for advertencia, explicacion in advertencias:
        doc.add_paragraph(f"Log: {advertencia}")
        doc.add_paragraph(f"Explicación: {explicacion}")
        doc.add_paragraph("\n")
    
    doc.add_heading("Sección 4.3: Análisis de Eventos Críticos", level=3)
    doc.add_paragraph("A continuación se detallan los eventos críticos encontrados durante el análisis:")
    for evento_critico, explicacion in eventos_criticos:
        doc.add_paragraph(f"Log: {evento_critico}")
        doc.add_paragraph(f"Explicación: {explicacion}")
        doc.add_paragraph("\n")
    
    # Distribución Temporal de Eventos
    doc.add_heading("5. Patrones Recurrentes", level=2)
    doc.add_paragraph(
        "En esta sección se identifican los patrones recurrentes de errores y advertencias "
        "que han ocurrido a lo largo del tiempo. Estos patrones pueden indicar problemas subyacentes "
        "que requieren una atención especial para mejorar la estabilidad y seguridad del sistema."
    )
    doc.add_paragraph("\n")
    
    # Conclusiones y Recomendaciones
    doc.add_heading("6. Conclusiones y Recomendaciones", level=2)
    doc.add_paragraph(
        "A partir del análisis de los logs, se identificaron varios problemas críticos que requieren atención inmediata. "
        "Es fundamental implementar medidas correctivas para evitar que los errores detectados afecten la estabilidad y seguridad del sistema. "
        "Se recomienda una revisión exhaustiva de los componentes del sistema implicados en los errores más comunes, así como la implementación de mejores prácticas "
        "para la monitorización y el mantenimiento preventivo."
    )
    
    # Firma del Auditor
    doc.add_heading("7. Firmas", level=2)
    doc.add_paragraph("Firma del Auditor: __________________________")
    doc.add_paragraph("Nombre del Auditor: [Nombre del Auditor]")
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
