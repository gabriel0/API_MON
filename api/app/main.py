from flask import Flask, request, jsonify
import subprocess
import psutil
import os

app = Flask(__name__)

# Endpoint para obtener métricas de uso del sistema
@app.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        # Obtener el uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        load_avg = os.getloadavg()
        load_average = {
            "1m": load_avg[0],
            "5m": load_avg[1],
            "15m": load_avg[2]
        }

        # Obtener el uso de memoria
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total / (1024 * 1024),  # Convertir a MB
            "available": memory.available / (1024 * 1024),  # Convertir a MB
            "percent": memory.percent,
            "used": memory.used / (1024 * 1024),  # Convertir a MB
            "free": memory.free / (1024 * 1024)  # Convertir a MB
        }

        # Obtener el uso del disco
        disk_usage = psutil.disk_usage('/')
        disk_info = {
            "total": disk_usage.total / (1024 * 1024 * 1024),  # Convertir a GB
            "used": disk_usage.used / (1024 * 1024 * 1024),  # Convertir a GB
            "free": disk_usage.free / (1024 * 1024 * 1024),  # Convertir a GB
            "percent": disk_usage.percent
        }

        # Obtener la utilización de red
        net_io = psutil.net_io_counters()
        network_usage = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv
        }

        return jsonify({
            "cpu_percent": cpu_percent,
            "load_avg": load_average,
            "memory_usage": memory_usage,
            "disk_usage": disk_info,
            "network_usage": network_usage
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener métricas', 'details': str(e)}), 500

# Endpoint para ejecutar el script Bash

@app.route('/run_script', methods=['POST'])
def run_script():
    data = request.json
    option = data.get('option')
    directory = data.get('directory', '')

    # Comando con la ruta completa
    command = f"/app/script.sh {option} {directory}"
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return jsonify({'details': result.stdout, 'error': None})
    except subprocess.CalledProcessError as e:
        return jsonify({'details': e.output, 'error': str(e)})


if __name__ == '__main__':
    port = int(os.getenv('FINAL_PORT', 5000))  # Lee el puerto desde la variable de entorno, o usa 5000 por defecto
    app.run(host='0.0.0.0', port=port)