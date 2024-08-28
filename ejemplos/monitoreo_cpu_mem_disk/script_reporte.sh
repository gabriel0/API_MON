#!/bin/bash

ARCHIVO_DATOS="datos_performance.csv"
REPORTE_DIARIO="reporte_diario_$(date +%Y-%m-%d).txt"

# Procesar datos y generar reporte
awk -F, '
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
' "$ARCHIVO_DATOS" > "$REPORTE_DIARIO"