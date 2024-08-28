#!/bin/bash

ARCHIVO_DATOS="datos_performance.csv"
REPORTE_DIARIO="reporte_diario_$(date +%Y-%m-%d).txt"
SERVER_NAME=$(hostname)

# Validar si el archivo de datos existe
if [ ! -f "$ARCHIVO_DATOS" ]; then
    echo "Error: El archivo de datos '$ARCHIVO_DATOS' no existe." >&2
    exit 1 
fi

# Procesar datos y generar reporte (si el archivo existe)
if ! awk -F, '
    NR>1 {
        cpu_user_sum+=$2; cpu_sys_sum+=$3; cpu_idle_sum+=$4; iowait_sum+=$5
        disk_read_sum+=$6; disk_write_sum+=$7
    }
    END {
        num_rows=NR-1
        cpu_user_avg=cpu_user_sum/num_rows; cpu_sys_avg=cpu_sys_sum/num_rows
        cpu_idle_avg=cpu_idle_sum/num_rows; iowait_avg=iowait_sum/num_rows
        disk_read_avg=disk_read_sum/num_rows; disk_write_avg=disk_write_sum/num_rows

        printf "Reporte de Performance del Servidor - %s\n\n", strftime("%Y-%m-%d")

        printf "CPU:\n"
        printf "* Uso promedio: %.1f%%\n", cpu_user_avg + cpu_sys_avg
        printf "* Uso máximo: [calcular desde datos]\n"
        printf "* Procesos con mayor uso: [obtener con 'ps' o similar]\n\n"

        printf "IO a Disco:\n"
        printf "* IOPS promedio (lectura/escritura): %.1f / %.1f\n", disk_read_avg, disk_write_avg
        printf "* Tasa de transferencia promedio: [calcular desde datos]\n"
        printf "* Latencia promedio: [obtener con 'iostat' o similar]\n"
        printf "* Dispositivos con mayor actividad: [obtener con 'iostat' o similar]\n\n"

        printf "Filesystems:\n"
        printf "* Filesystem | Tamaño Total | Usado | Disponible | %% Uso\n"
        printf "* %s | %s | %s | %s | %.1f%%\n", $8, $9, $10, 100*$9/$8 
        # Repetir para otros filesystems si es necesario

        printf "\nIO Wait:\n"
        printf "* Promedio: %.1f%%\n", iowait_avg
        printf "* Máximo: [calcular desde datos]\n"
    }
' "$ARCHIVO_DATOS" > "$REPORTE_DIARIO" 2>&1; then
    # Loguear el error si comando awk fallo
    echo "Error al generar el reporte: $?" >&2
    mail -s "Error en reporte de performance $SERVER_NAME" destinatario@ejemplo.com
else
    # Enviar el reporte por correo si no hubo errores
    mail -s "Reporte de Performance $SERVER_NAME $(date +%Y-%m-%d)" destinatario@ejemplo.com < "$REPORTE_DIARIO" 
fi