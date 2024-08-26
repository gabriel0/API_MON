#!/bin/bash

# Script unificado para listar procesos ordenados por uso de CPU o memoria
# y mostrar el uso de espacio de carpetas en el primer nivel de un directorio

# Función para mostrar el uso del script
usage() {
  echo "Uso: $0 [cpu|mem|disk] [ruta_del_directorio (solo si se selecciona 'disk')]"
  echo "  cpu: Mostrar los procesos ordenados por uso de CPU"
  echo "  mem: Mostrar los procesos ordenados por uso de memoria"
  echo "  disk: Mostrar el uso de espacio de las carpetas en el primer nivel de un directorio"
  echo "Ejemplo para procesos por CPU: $0 cpu"
  echo "Ejemplo para procesos por memoria: $0 mem"
  echo "Ejemplo para uso de filesystem: $0 disk /home/usuario"
  exit 1
}

# Verificar si se ha proporcionado al menos un argumento
if [ "$#" -lt 1 ]; then
  usage
fi

# Variables para opciones y ruta del directorio
option="$1"
directory="$2"

# Función para listar procesos por uso de CPU o memoria
list_processes() {
  local sort_option=""
  case $1 in
    cpu)
      sort_option="-%cpu"
      echo "Listando procesos por uso de CPU:"
      ;;
    mem)
      sort_option="-%mem"
      echo "Listando procesos por uso de memoria:"
      ;;
    *)
      usage
      ;;
  esac

  # Mostrar el encabezado para mejor legibilidad
  echo "PID %CPU %MEM COMMAND"

  # Utilizar ps para listar procesos y ordenarlos según la opción seleccionada
  ps -eo pid,%cpu,%mem,cmd --sort=$sort_option | grep -v -E "ps -eo|head -n|sh /app/script.sh" | head -n 10

}

# Función para listar el uso de espacio de carpetas en el primer nivel de un directorio
list_filesystem_usage() {
  if [ -z "$1" ]; then
    echo "Error: Debes proporcionar una ruta de directorio para listar su uso de espacio."
    exit 1
  fi

  if [ ! -d "$1" ]; then
    echo "Error: $1 no es un directorio válido."
    exit 1
  fi

  echo "Tamaño de las carpetas en el primer nivel de anidacion en $1:"
  du -sh "$1"/*
}

# Lógica principal para ejecutar las funciones basadas en la opción proporcionada
case $option in
  cpu|mem)
    list_processes $option
    ;;
  disk)
    if [ -z "$directory" ]; then
      echo "Error: Debes proporcionar una ruta de directorio para listar su uso de espacio."
      usage
    fi
    list_filesystem_usage $directory
    ;;
  *)
    usage
    ;;
esac