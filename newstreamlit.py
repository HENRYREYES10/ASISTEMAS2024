import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from datetime import datetime
from collections import Counter

# Función para leer los logs desde el archivo subido
def leer_logs(file_path):
    try:
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.readlines()
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return []

# Función para generar explicaciones detalladas para cada tipo de log
def generar_explicacion(log):
    if "Database connection failed" in log:
        return "Error en la conexión con la base de datos. Verificar credenciales y estado del servicio."
    elif "Unable to reach API endpoint" in log:
        return "Fallo al comunicar con el endpoint de la API. Revisar conectividad de red."
    elif "Failed to back up database" in log:
        return "Copia de seguridad de la base de datos fallida. Posibles problemas de espacio en disco o permisos."
    else:
        return "Evento registrado que requiere revisión."

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

# Función para generar un resumen estadístico de los logs
def generar_resumen(errores, advertencias, eventos_criticos, otros_eventos):
    return {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Errores más comunes': Counter([log[0] for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([log[0] for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([log[0] for log in eventos_criticos]).most_common(5),
        'Fecha del resumen': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Función para generar el informe de auditoría en formato Word
def generar_informe_word(resumen, errores, advertencias, eventos_criticos, nombre_auditor):
    document = Document()
    
    # Carátula del informe
    document.add_heading("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA", 0)
    document.add_paragraph(f"Fecha de Generación: {resumen['Fecha del resumen']}")
    document.add_paragraph(f"Auditor: {nombre_auditor}")
    document.add_paragraph(f"Total de Logs Analizados: {resumen['Total de logs']}")
    
    # Introducción
    document.add_heading("Introducción", level=1)
    document.add_paragraph(
        "Este informe detalla los hallazgos de la auditoría de logs realizada en el sistema. "
        "Los logs son registros críticos para la identificación de problemas de seguridad, "
        "rendimiento y operación de la infraestructura tecnológica."
    )
    
    # Análisis de Resultados
    document.add_heading("Resultados de la Auditoría", level=1)
    document.add_paragraph(f"Total de Errores detectados: {resumen['Errores']}")
    document.add_paragraph(f"Total de Advertencias detectadas: {resumen['Advertencias']}")
    document.add_paragraph(f"Total de Eventos Críticos detectados: {resumen['Eventos críticos']}")
    
    # Detalles específicos
    document.add_heading("Detalles Específicos de Errores", level=2)
    for log, explicacion in errores:
        document.add_paragraph(f"{log}: {explicacion}")
    
    document.add_heading("Detalles Específicos de Advertencias", level=2)
    for log, explicacion in advertencias:
        document.add_paragraph(f"{log}: {explicacion}")
    
    document.add_heading("Detalles Específicos de Eventos Críticos", level=2)
    for log, explicacion in eventos_criticos:
        document.add_paragraph(f"{log}: {explicacion}")
    
    # Conclusiones
    document.add_heading("Conclusiones y Recomendaciones", level=1)
    document.add_paragraph(
        "Se recomienda revisar los problemas detectados y tomar medidas correctivas para mejorar la seguridad y estabilidad del sistema. "
        "La implementación de mejores prácticas y la revisión periódica de logs ayudarán a minimizar futuros riesgos."
    )
    
    # Guardar el documento
    document.save("Informe_Auditoria_Logs.docx")
    messagebox.showinfo("Informe Generado", "El informe se ha generado correctamente.")

# Clase de la interfaz gráfica
class AuditoriaLogsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auditoría de Logs del Sistema")
        self.geometry("600x400")
        self.logs_path = ""
        self.nombre_auditor = ""
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Auditoría de Logs del Sistema", font=("Helvetica", 16))
        self.label.pack(pady=20)
        
        self.logs_button = tk.Button(self, text="Seleccionar Archivo de Logs", command=self.seleccionar_archivo)
        self.logs_button.pack(pady=10)
        
        self.nombre_auditor_button = tk.Button(self, text="Ingresar Nombre del Auditor", command=self.ingresar_nombre_auditor)
        self.nombre_auditor_button.pack(pady=10)
        
        self.generar_button = tk.Button(self, text="Generar Informe", command=self.generar_informe)
        self.generar_button.pack(pady=20)

    def seleccionar_archivo(self):
        self.logs_path = tk.filedialog.askopenfilename(title="Seleccionar Archivo de Logs", filetypes=[("Archivos de Logs", "*.log")])
        if self.logs_path:
            messagebox.showinfo("Archivo Seleccionado", f"Archivo de Logs seleccionado: {self.logs_path}")

    def ingresar_nombre_auditor(self):
        self.nombre_auditor = simpledialog.askstring("Nombre del Auditor", "Ingrese el nombre del auditor:")
        if self.nombre_auditor:
            messagebox.showinfo("Nombre del Auditor", f"Auditor: {self.nombre_auditor}")

    def generar_informe(self):
        if not self.logs_path or not self.nombre_auditor:
            messagebox.showerror("Error", "Debe seleccionar un archivo de logs y proporcionar el nombre del auditor.")
            return
        
        logs = leer_logs(self.logs_path)
        if not logs:
            messagebox.showerror("Error", "No se pudo leer el archivo de logs.")
            return
        
        errores, advertencias, eventos_criticos, otros_eventos = analizar_logs(logs)
        resumen = generar_resumen(errores, advertencias, eventos_criticos, otros_eventos)
        generar_informe_word(resumen, errores, advertencias, eventos_criticos, self.nombre_auditor)

if __name__ == "__main__":
    app = AuditoriaLogsApp()
    app.mainloop()
