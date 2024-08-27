from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import subprocess
import psutil
import os
import jwt

app = Flask(__name__, static_folder='assets')

SECRET_KEY = str(os.getenv('SECRET_KEY'))
MASTER_KEY = str(os.getenv('MASTER_KEY'))

# Función para generar el token
def generate_token():
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=5)  # Expira en 5 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Decorador para requerir el token (corregido)
def require_token(func):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token faltante'}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        return func(*args, **kwargs)
    decorated_function.__name__ = func.__name__  # Asigna el nombre original, para evitar el overlap de nombre de funciones
    return decorated_function

# Ruta para documentación (apidocjs)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Endpoint para obtener el token (protegido con clave maestra)
@app.route('/get_token', methods=['POST'])
def get_token():
    """
    @api {post} /get_token Devuelve un token para el uso de los metodos expuestos por esta api
    @apiName get_token
    @apiVersion 1.0.0
    @apiGroup autorizaciones
    @apiHeader {String} master_key master key que permite obtener un token
    @apiSuccess {json} Result Devuelve un token
    @apiSuccessExample {json} Success-Response:
        [
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjQ2OTUxMzF9.F8GA_soxzWSkjhJve5mxQWy0gfuIF3nuOPGvr-sF824"
            }
        ]
    """
    data = request.json
    provided_key = data.get('master_key')

    if provided_key != MASTER_KEY:
        return jsonify({'error': 'Clave maestra incorrecta'}), 401

    token = generate_token()
    return jsonify({'token': token})

# Endpoint para obtener métricas de uso del sistema (protegido)
@app.route('/metrics', methods=['GET'])
@require_token 
def get_metrics():
    """
    @api {get} /metrics Lista metricas de cpu, memoria, disco con sus valores
    @apiName metrics
    @apiVersion 1.0.0
    @apiGroup metricas
    @apiHeader {String} Authorization Token JWT obtenido de /get_token
    @apiSuccess {json} Result Devuelve una respuesta en formato json con los valores de cada metrica
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

# Endpoint para ejecutar el script Bash (protegido)
@app.route('/run_script', methods=['POST'])
@require_token 
def run_script():
    """
    @api {post} /run_script Permite invocar un script con sus parametros
    @apiName run_script
    @apiVersion 1.0.0
    @apiGroup scripts
    @apiHeader {String} Authorization Token JWT obtenido de /get_token
    @apiParam {json} option Indicar el tipo de opcion: "cpu, disk, mem"
    @apiSuccess {String} Result Devuelve una lista en formato string de datos relacionados al tipo de "option"
    @apiSuccessExample {String} Success-Response:
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
    port = int(os.getenv('FINAL_PORT'))  # Lee el puerto desde la variable de entorno
    app.run(host='0.0.0.0', port=port)