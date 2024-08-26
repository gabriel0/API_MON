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
    try:
        # Obtener los datos del cuerpo de la solicitud POST
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibió contenido JSON en la solicitud'}), 400

        # Imprimir datos recibidos para depuración
        print(f"Datos recibidos: {data}")

        if 'option' not in data:
            return jsonify({'error': 'Falta el parámetro "option" en la solicitud', 'data_received': data}), 400

        option = data['option']
        directory = data.get('directory', '')

        # Validar la opción proporcionada
        if option not in ['cpu', 'mem', 'disk']:
            return jsonify({'error': 'Opción no válida. Debe ser "cpu", "mem" o "disk".', 'option_received': option}), 400

        # Construir el comando a ejecutar
        command = ['./app/script.sh', option]
        
        # Añadir el directorio si la opción es 'disk'
        if option == 'disk':
            if not directory:
                return jsonify({'error': 'Se requiere un directorio para la opción "disk".', 'directory_received': directory}), 400
            command.append(directory)

        # Ejecutar el script Bash con los argumentos proporcionados
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Devolver la salida del script como respuesta JSON
        return jsonify({'output': result.stdout}), 200

    except subprocess.CalledProcessError as e:
        # Manejar errores en la ejecución del script
        return jsonify({'error': 'Error al ejecutar el script', 'details': e.stderr}), 500
    except Exception as e:
        # Manejar errores genéricos
        return jsonify({'error': 'Error al procesar la solicitud', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FINAL_PORT', 5000))  # Lee el puerto desde la variable de entorno, o usa 5000 por defecto
    app.run(host='0.0.0.0', port=port)