from flask import Flask, request, jsonify, send_from_directory
import subprocess
import psutil
import os

app = Flask(__name__, static_folder='assets') 

# Ruta para documentación
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Endpoint para obtener métricas de uso del sistema
@app.route('/metrics', methods=['GET'])
def get_metrics():
    """
    @api {get} /metrics Lista metricas de cpu, memoria, disco con sus valores
    @apiName metrics
    @apiVersion 1.0.0
    @apiGroup metricas
    @apiSuccess {json} Result Devueve una respuesta en formato json con los valores de cada metrica
    @apiSuccessExample {json} Success-Response:
        [
            {
                "cpu_percent": 14.4,
                "disk_usage": {
                    "free": 945.9212875366211,
                    "percent": 1,
                    "total": 1006.853931427002,
                    "used": 9.717021942138672
                },
                "load_avg": {
                    "15m": 0.0703125,
                    "1m": 0.09716796875,
                    "5m": 0.0712890625
                },
                "memory_usage": {
                    "available": 6659.40625,
                    "free": 5313.76171875,
                    "percent": 14.1,
                    "total": 7748.07421875,
                    "used": 837.3203125
                },
                "network_usage": {
                    "bytes_recv": 1939,
                    "bytes_sent": 256
                }
            }
        ]
    """    
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
    """
    @api {post} /run_script Permite invocar un script con sus parametros
    @apiName run_script
    @apiVersion 1.0.0
    @apiGroup scripts
    @apiParam {json} option Indicar el tipo de opcion: "cpu, disk, mem"
    @apiSuccess {json} Result Devuelve una lista en formato string de datos relacionados al tipo de "option"
    @apiSuccessExample {json} Success-Response:
        [
            {
                "details":"Tamaño de las carpetas en el primer nivel de anidacion en /app:
                4.0K /app/check_and_download.py
                4.0K /app/main.py
                4.0K /app/script.sh",
            }
        ]
    """    
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
    app.run(host='0.0.0.0', port=port, debug=True)