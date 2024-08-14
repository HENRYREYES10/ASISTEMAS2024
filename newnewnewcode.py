import streamlit as st
from fpdf import FPDF
from io import BytesIO

def generar_informe_pdf(resumen, errores, advertencias, eventos_criticos, total_logs):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", ln=True, align='C')

    pdf.cell(200, 10, txt=f"Fecha: {resumen['Fecha del resumen']}", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Total de Logs Analizados: {total_logs}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Errores: {resumen['Errores']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Advertencias: {resumen['Advertencias']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Eventos Críticos: {resumen['Eventos críticos']}", ln=True, align='L')
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Detalle de Errores", ln=True, align='L')
    for log, explicacion in errores:
        pdf.multi_cell(0, 10, f"Log: {log}\nExplicación: {explicacion}", align='L')
        pdf.ln(5)

    pdf.cell(200, 10, txt="Detalle de Advertencias", ln=True, align='L')
    for log, explicacion in advertencias:
        pdf.multi_cell(0, 10, f"Log: {log}\nExplicación: {explicacion}", align='L')
        pdf.ln(5)

    pdf.cell(200, 10, txt="Detalle de Eventos Críticos", ln=True, align='L')
    for log, explicacion in eventos_criticos:
        pdf.multi_cell(0, 10, f"Log: {log}\nExplicación: {explicacion}", align='L')
        pdf.ln(5)

    # Guardar el PDF en un buffer en memoria
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return buffer

def main():
    st.title("Auditoría de Logs del Sistema")
    archivos_subidos = st.file_uploader("Seleccione los archivos de logs", accept_multiple_files=True, type="log")

    if archivos_subidos:
        # Aquí iría el código para leer los logs, analizarlos y generar el resumen
        # Vamos a simular algunos resultados para esta demostración
        resumen = {'Fecha del resumen': '2024-08-14', 'Errores': 3, 'Advertencias': 2, 'Eventos críticos': 1}
        errores = [("2024-08-10 10:01:00 ERROR Database connection failed", "Error grave en la base de datos.")]
        advertencias = [("2024-08-10 11:00:00 WARNING High memory usage detected", "Advertencia sobre uso de memoria.")]
        eventos_criticos = [("2024-08-10 10:02:00 CRITICAL System outage detected", "Caída del sistema detectada.")]
        total_logs = 10

        if st.button("Generar Informe"):
            buffer = generar_informe_pdf(resumen, errores, advertencias, eventos_criticos, total_logs)
            st.download_button(label="Descargar Informe PDF", data=buffer, file_name="informe_auditoria_logs.pdf")

if __name__ == "__main__":
    main()
