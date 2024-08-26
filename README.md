# API_MON

## Lenguaje y frameworks utilizados

## Uso de run_script:

### Listar procesos por uso de memoria:
- curl -X POST -H "Content-Type: application/json" -d '{"option": "mem"}' http://localhost:5000/run_script

### Listar uso de disco por carpetas (L1):
- curl -X POST -H "Content-Type: application/json" -d '{"option": "disk", "directory": "/"}' http://localhost:5000/run_script

### Listar procesos por uso de cpu:
- curl -X POST -H "Content-Type: application/json" -d '{"option": "cpu"}' http://localhost:5000/run_script

## Construccion de imagen
- Ejecutar un docker build . -t IMAGEN:TAG

## Acceso a la imagen
- http://localhost:5000