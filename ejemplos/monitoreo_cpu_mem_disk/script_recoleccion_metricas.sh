#!/bin/bash

# Configuración
INTERVALO=300 # Intervalo de recolección de datos en segundos (5 minutos)
ARCHIVO_DATOS="datos_performance.csv"

# Cabecera del archivo de datos (si no existe)
if [ ! -f "$ARCHIVO_DATOS" ]; then
    echo "timestamp,cpu_user,cpu_sys,cpu_idle,iowait,disk_read,disk_write,fs_total,fs_used,fs_avail" > "$ARCHIVO_DATOS"
fi

while true; do
    timestamp=$(date +%s)

    # CPU
    # mpstat 1 2, toma dos muestras con intervalo de 1 segundo esto se debe ajustar segun necesidades
    # awk '/Average:/ {print $3,$4,$12,$16}, se queda con la linea Average que es el promedio de las muestras y luego imprime las columnas 3 (cpu_user) 4 (cpu_sys) 12 (cpu_idle) 16 (iowait)
    # Guardamos los resultados en un array cpu_stats el cual es accedido en sus distintas posiciones 0,1,2,3 .... para asignarlo a la variables especifica
    cpu_stats=($(mpstat 1 2 | awk '/Average:/ {print $3,$4,$12,$16}'))
    cpu_user=${cpu_stats[0]}
    cpu_sys=${cpu_stats[1]}
    cpu_idle=${cpu_stats[2]}
    iowait=${cpu_stats[3]}

    # IO a Disco
    # iostat -d 1 2, toma dos muestras con un intervalo de 1 segundo esto se debe ajustar a la necesidad.
    # awk '/sda/ && NR==4 {print $4,$5}, se queda con los dispositivos sda, se queda con la linea 4 para evitar loguear los encabezados e imprime las columnas 4 (read stats) y 5 (write stats)
    # Guardamos los resultados en un array disk_stats el cual es accedido en sus distintas posiciones 0,1,2,3 .... para asignarlo a la variables especifica
    disk_stats=($(iostat -d 1 2 | awk '/sda/ && NR==4 {print $4,$5}')) # Ajustar 'sda' si es necesario
    disk_read=${disk_stats[0]}
    disk_write=${disk_stats[1]}

    # Filesystems
    # df -h, lista los filesystems en formato human para mejor lectura muestra MB, GB, etc en lugar de bytes
    # awk '/\/$/, Se queda con el disco raiz (/)
    # {print $2,$3,$4}, Del disco, en este caso, raiz. Imprime columnas 2 (fs_total) 3 (fs_used) 4 (fs_available)
    # Guardamos los resultados en un array fs_stats el cual es accedido en sus distintas posiciones 0,1,2,3 .... para asignarlo a la variables especifica
    fs_stats=($(df -h | awk '/\/$/ {print $2,$3,$4}')) # Considera solo el filesystem raíz '/'
    fs_total=${fs_stats[0]}
    fs_used=${fs_stats[1]}
    fs_avail=${fs_stats[2]}

    # Almacena datos en archivo
    echo "$timestamp,$cpu_user,$cpu_sys,$cpu_idle,$iowait,$disk_read,$disk_write,$fs_total,$fs_used,$fs_avail" >> "$ARCHIVO_DATOS"

    sleep "$INTERVALO"
done