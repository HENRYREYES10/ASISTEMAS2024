import os
import re
from collections import Counter
import datetime
from tkinter import Tk, filedialog

# Función para leer un archivo de logs
def leer_logs(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='latin-1') as file:
            logs = file.readlines()
        return logs
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no se encontró.")
    except PermissionError:
        print(f"Error: No se tienen permisos para leer el archivo {ruta_archivo}.")
    except Exception as e:
        print(f"Error inesperado al leer el archivo {ruta_archivo}: {e}")
        return []

# Función para generar una explicación para cada error o advertencia
def generar_explicacion(log):
    if 'ERROR' in log:
        return "Este es un error del sistema, lo que significa que ocurrió un fallo inesperado en el proceso o en la aplicación que requiere atención inmediata."
    elif 'WARNING' in log:
        return "Este es una advertencia, lo que indica un posible problema que no interrumpió la ejecución, pero que podría causar problemas en el futuro si no se aborda."
    elif 'CRITICAL' in log:
        return "Este es un evento crítico, que normalmente señala un fallo grave en el sistema que puede requerir acciones inmediatas para evitar un impacto mayor."
    else:
        return "Evento registrado sin mayor categoría, que podría representar un evento rutinario o un estado informativo."

# Función para analizar los logs y generar explicaciones
def analizar_logs(logs):
    errores = []
    advertencias = []
    eventos_criticos = []
    otros_eventos = []

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

# Función para combinar los resultados de múltiples archivos de logs
def combinar_resultados(resultados):
    errores = []
    advertencias = []
    eventos_criticos = []
    otros_eventos = []

    for resultado in resultados:
        errores.extend(resultado[0])
        advertencias.extend(resultado[1])
        eventos_criticos.extend(resultado[2])
        otros_eventos.extend(resultado[3])

    return errores, advertencias, eventos_criticos, otros_eventos

# Función auxiliar para obtener la tercera palabra o la hora de un log
def obtener_tercera_palabra(log):
    palabras = log.split()
    return palabras[2] if len(palabras) > 2 else 'Desconocido'

def obtener_hora(log):
    try:
        return log.split(' ')[1].split(':')[0]
    except IndexError:
        return 'Desconocido'

# Función para generar un resumen de los logs
def generar_resumen(errores, advertencias, eventos_criticos, otros_eventos):
    resumen = {
        'Total de logs': len(errores) + len(advertencias) + len(eventos_criticos) + len(otros_eventos),
        'Errores': len(errores),
        'Advertencias': len(advertencias),
        'Eventos críticos': len(eventos_criticos),
        'Otros eventos': len(otros_eventos),
        'Errores más comunes': Counter([obtener_tercera_palabra(log[0]) for log in errores]).most_common(5),
        'Advertencias más comunes': Counter([obtener_tercera_palabra(log[0]) for log in advertencias]).most_common(5),
        'Eventos críticos más comunes': Counter([obtener_tercera_palabra(log[0]) for log in eventos_criticos]).most_common(5),
        'Frecuencia de errores por hora': Counter([obtener_hora(log[0]) for log in errores]),
        'Frecuencia de advertencias por hora': Counter([obtener_hora(log[0]) for log in advertencias]),
        'Frecuencia de eventos críticos por hora': Counter([obtener_hora(log[0]) for log in eventos_criticos]),
        'Fecha del resumen': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return resumen

# Función para generar un informe de auditoría
def generar_informe(resumen, archivo_salida, objetivo_prueba, errores, advertencias, eventos_criticos):
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as file:
            # Escribir la teoría sobre los logs
            file.write("INFORME DE AUDITORÍA DE LOGS DEL SISTEMA\n")
            file.write("=======================================\n\n")
            
            teoria = """
            ============================
            TEORÍA SOBRE LOS LOGS DEL SISTEMA
            ============================

            Los logs son registros de eventos que ocurren en un sistema, aplicación o dispositivo. Estos registros contienen información detallada sobre 
            las actividades que se realizan, como errores, advertencias, accesos, transacciones, y otros eventos importantes. 

            Los logs son fundamentales para la monitorización, auditoría, y diagnóstico de sistemas. Ayudan a los administradores y desarrolladores a 
            revisar el comportamiento del sistema y detectar posibles problemas o irregularidades.

            Propósitos principales de los logs:
            1. Monitorización: Permiten un monitoreo continuo de la actividad del sistema, ayudando a detectar problemas en tiempo real.
            2. Diagnóstico de Problemas: Proporcionan la información necesaria para diagnosticar y solucionar problemas.
            3. Auditoría y Cumplimiento: Sirven como evidencia en auditorías para cumplir con regulaciones legales.
            4. Seguridad: Registran intentos de acceso, actividades sospechosas, y otros eventos que podrían indicar una brecha de seguridad.
            5. Análisis de Rendimiento: Ayudan a identificar cuellos de botella y áreas que necesitan optimización.
            6. Trazabilidad y Depuración: Facilitan la identificación de errores en el código durante el desarrollo de software.

            ============================
            """
            file.write(teoria)

            file.write("\nOBJETIVO DE LA PRUEBA\n")
            file.write("=======================\n")
            file.write(f"{objetivo_prueba}\n\n")
            
            file.write(f"Fecha del informe: {resumen['Fecha del resumen']}\n")
            file.write(f"Total de logs analizados: {resumen['Total de logs']}\n\n")
            
            file.write("1. RESUMEN DE RESULTADOS\n")
            file.write("------------------------\n")
            file.write(f"Total de Errores: {resumen['Errores']}\n")
            file.write(f"Total de Advertencias: {resumen['Advertencias']}\n")
            file.write(f"Total de Eventos Críticos: {resumen['Eventos críticos']}\n")
            file.write(f"Total de Otros Eventos: {resumen['Otros eventos']}\n\n")
            
            file.write("2. ANÁLISIS DE ERRORES MÁS COMUNES\n")
            file.write("----------------------------------\n")
            for error in resumen.get('Errores más comunes', []):
                file.write(f"{error[0]}: {error[1]} ocurrencias\n")
            
            file.write("\n3. ANÁLISIS DE ADVERTENCIAS MÁS COMUNES\n")
            file.write("---------------------------------------\n")
            for advertencia in resumen.get('Advertencias más comunes', []):
                file.write(f"{advertencia[0]}: {advertencia[1]} ocurrencias\n")
            
            file.write("\n4. ANÁLISIS DE EVENTOS CRÍTICOS MÁS COMUNES\n")
            file.write("-------------------------------------------\n")
            for evento in resumen.get('Eventos críticos más comunes', []):
                file.write(f"{evento[0]}: {evento[1]} ocurrencias\n")
            
            file.write("\n5. DISTRIBUCIÓN TEMPORAL DE EVENTOS\n")
            file.write("-----------------------------------\n")
            file.write("Frecuencia de Errores por Hora:\n")
            for hora, frecuencia in sorted(resumen.get('Frecuencia de errores por hora', {}).items()):
                file.write(f"{hora}:00 - {frecuencia} errores\n")
            
            file.write("\nFrecuencia de Advertencias por Hora:\n")
            for hora, frecuencia in sorted(resumen.get('Frecuencia de advertencias por hora', {}).items()):
                file.write(f"{hora}:00 - {frecuencia} advertencias\n")
            
            file.write("\nFrecuencia de Eventos Críticos por Hora:\n")
            for hora, frecuencia in sorted(resumen.get('Frecuencia de eventos críticos por hora', {}).items()):
                file.write(f"{hora}:00 - {frecuencia} eventos críticos\n")

            file.write("\n6. DETALLE DE ERRORES Y PROBLEMAS ENCONTRADOS\n")
            file.write("---------------------------------------------\n")
            file.write("A continuación se presentan los detalles de los errores, advertencias y eventos críticos encontrados, junto con una explicación:\n\n")

            file.write("ERRORES:\n")
            for log, explicacion in errores:
                file.write(f"{log}\nExplicación: {explicacion}\n\n")
            
            file.write("ADVERTENCIAS:\n")
            for log, explicacion in advertencias:
                file.write(f"{log}\nExplicación: {explicacion}\n\n")
            
            file.write("EVENTOS CRÍTICOS:\n")
            for log, explicacion in eventos_criticos:
                file.write(f"{log}\nExplicación: {explicacion}\n\n")
            
            file.write("\nEste informe proporciona una visión general del estado actual del sistema basado en los logs analizados. Se recomienda seguir las acciones correctivas propuestas y realizar un seguimiento regular para asegurar la estabilidad y seguridad del sistema.\n")
    except PermissionError:
        print(f"Error: No se pudo escribir en el archivo {archivo_salida} debido a permisos insuficientes.")
    except Exception as e:
        print(f"Error inesperado al generar el informe: {e}")

# Función para seleccionar archivos de logs usando una ventana emergente
def seleccionar_archivos():
    Tk().withdraw()  # Cerrar la ventana raíz de tkinter
    archivos = filedialog.askopenfilenames(
        title="Seleccione los archivos de logs",
        filetypes=[("Archivos de log", "*.log"), ("Todos los archivos", "*.*")]
    )
    return list(archivos)

# Main script
def main():
    print("Auditoría de Logs del Sistema")

    # Ingresar el objetivo de la prueba
    objetivo_prueba = input("Ingrese el objetivo de la prueba: ")

    # Seleccionar archivos
    rutas_archivos = seleccionar_archivos()

    if rutas_archivos:
        resultados = []

        for ruta in rutas_archivos:
            logs = leer_logs(ruta)
            if logs:
                resultados.append(analizar_logs(logs))
        
        # Combinar los resultados de todos los archivos de logs
        errores, advertencias, eventos_criticos, otros_eventos = combinar_resultados(resultados)

        # Generar el resumen
        resumen = generar_resumen(errores, advertencias, eventos_criticos, otros_eventos)

        # Mostrar el resumen en la consola
        print("\nResumen de Resultados")
        print("=====================")
        for key, value in resumen.items():
            print(f"{key}: {value}")

        # Guardar el informe
        archivo_salida = os.path.join(os.path.dirname(rutas_archivos[0]), 'informe_auditoria_logs.txt')
        generar_informe(resumen, archivo_salida, objetivo_prueba, errores, advertencias, eventos_criticos)
        print(f"\nInforme de auditoría generado: {archivo_salida}")

    else:
        print("No se seleccionaron archivos de logs.")

if __name__ == "__main__":
    main()
