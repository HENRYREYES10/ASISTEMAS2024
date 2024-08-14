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
    errores_explicaciones = {
        'Database connection failed': "El sistema no pudo establecer una conexión con la base de datos...",
        'Unable to reach API endpoint': "El sistema no pudo comunicarse con el punto final de API...",
        'Failed to back up database': "El respaldo de la base de datos no se pudo completar...",
        'High memory usage detected': "El sistema está utilizando una cantidad inusualmente alta de memoria...",
        'Disk space low': "El espacio en disco está llegando al límite...",
        'Slow response time': "El tiempo de respuesta del sistema es más lento de lo esperado...",
        'System outage detected': "Se ha detectado una interrupción del sistema...",
        'Security breach detected': "Se ha detectado una posible brecha de seguridad...",
        'Application crash': "Una aplicación del sistema se ha bloqueado inesperadamente..."
    }

    for clave, explicacion in errores_explicaciones.items():
        if clave in log:
            return explicacion

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
    return {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Errores más comunes': Counter([log.split(' ')[-1] for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([log.split(' ')[-1] for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([log.split(' ')[-1] for log in eventos_criticos]).most_common(5),
        'Frecuencia de errores por hora': Counter([log.split(' ')[1] for log in errores]),
        'Frecuencia de advertencias por hora': Counter([log.split(' ')[1] for log in advertencias]),
        'Frecuencia de eventos críticos por hora': Counter([log.split(' ')[1] for log in eventos_criticos]),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generar_informe_word(resumen, objetivo_prueba, errores, advertencias, eventos_criticos, total_logs):
    doc = Document()

    doc.add_heading("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", level=1)
    doc.add_paragraph(f"Fecha: {resumen['Fecha del resumen']}")
    doc.add_paragraph(f"Total de Logs Analizados: {total_logs}")

    doc.add_heading("Errores", level=2)
    for log, explicacion in errores:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")

    doc.add_heading("Advertencias", level=2)
    for log, explicacion in advertencias:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")

    doc.add_heading("Eventos Críticos", level=2)
    for log, explicacion in eventos_criticos:
        doc.add_paragraph(f"Log: {log}")
        doc.add_paragraph(f"Explicación: {explicacion}")

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
        objetivo_prueba = generar_objetivo_prueba(errores, advertencias, eventos_criticos)

        st.subheader("Resumen de Resultados")
        st.write(f"Total de Logs Analizados: {total_logs}")
        st.write(f"Errores: {resumen['Errores']}")
        st.write(f"Advertencias: {resumen['Advertencias']}")
        st.write(f"Eventos Críticos: {resumen['Eventos críticos']}")

        if st.button("Generar Informe"):
            buffer = generar_informe_word(resumen, objetivo_prueba, errores, advertencias, eventos_criticos, total_logs)
            st.download_button(label="Descargar Informe", data=buffer, file_name="informe_auditoria_logs.docx")

if __name__ == "__main__":
    main()
