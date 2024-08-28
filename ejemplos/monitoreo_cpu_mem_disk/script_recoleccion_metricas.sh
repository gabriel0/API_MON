#!/bin/bash

# Configuración
INTERVALO=300 # Intervalo de recolección de datos en segundos (5 minutos)
ARCHIVO_DATOS="datos_performance.csv"
REPORTE_DIARIO="reporte_diario.txt"

# Cabecera del archivo de datos (si no existe)
if [ ! -f "$ARCHIVO_DATOS" ]; then
    echo "timestamp,cpu_user,cpu_sys,cpu_idle,iowait,disk_read,disk_write,fs_total,fs_used,fs_avail" > "$ARCHIVO_DATOS"
fi

while true; do
    timestamp=$(date +%s)

    # CPU
    cpu_stats=($(mpstat 1 1 | awk '/Average:/ {print $3,$4,$12,$16}'))
    cpu_user=${cpu_stats[0]}
    cpu_sys=${cpu_stats[1]}
    cpu_idle=${cpu_stats[2]}
    iowait=${cpu_stats[3]}

    # IO a Disco
    disk_stats=($(iostat -d 1 2 | awk '/sda/ && NR==4 {print $4,$5}')) # Ajustar 'sda' si es necesario
    disk_read=${disk_stats[0]}
    disk_write=${disk_stats[1]}

    # Filesystems
    fs_stats=($(df -h | awk '/\/$/ {print $2,$3,$4}')) # Considera solo el filesystem raíz '/'
    fs_total=${fs_stats[0]}
    fs_used=${fs_stats[1]}
    fs_avail=${fs_stats[2]}

    # Almacenar datos
    echo "$timestamp,$cpu_user,$cpu_sys,$cpu_idle,$iowait,$disk_read,$disk_write,$fs_total,$fs_used,$fs_avail" >> "$ARCHIVO_DATOS"

    sleep "$INTERVALO"
done