# API_MON

## Lenguaje y frameworks utilizados

### Lenguaje

[python 3.9](https://www.python.org/)

### Framework

[Flask](https://flask.palletsprojects.com/en/3.0.x/)

### Documentacion API

[apiDocjs](https://apidocjs.com/)

## Funciones

- check_and_download:
    Este metodo valida que el script.sh, almacenado en este caso en S3 (aws), esté actualizado y en caso de haber cambios lo descarga y remplaza el actual. L intención es mantener actualizado el script de multiples instancias para evitar re-construir la imagen con cada cambio de script

- main:
    Es la funcion principal de la API, la cual entrega una lista de metricas.

## Actualizacion de la documentacion (apidocjs)

Posicionado en la raiz del proyecto (/app), ejecutar: "apidoc -i ./ -o ./"

## Construccion de imagen

Ejecutar un docker build . -t IMAGEN:TAG --build-arg port=5000

## Ejecucio de la imagen

docker run -d -p HOST_PORT:CONTAINER_PORT IMAGEN:TAG

## Acceso a la imagen

http://localhost:$port

## Uso de run_script

### Listar procesos por uso de memoria

```powershell
    #WINDOWS
    Remove-Item Env:http_proxy
    Remove-Item Env:https_proxy
    curl -X POST -H "Content-Type: application/json" -d '{"option": "mem"}' http://localhost:5000/run_script
```

```bash
    #LINUX
    export http_proxy=""
    export https_proxy=""
    curl -X POST -H "Content-Type: application/json" -d '{"option": "mem"}' http://localhost:5000/run_script
```

### Listar uso de disco por carpetas (L1)

```powershell
    #WINDOWS
    Remove-Item Env:http_proxy
    Remove-Item Env:https_proxy
    curl -X POST -H "Content-Type: application/json" -d '{"option": "disk", "directory": "/"}' http://localhost:5000/run_script
```

```bash
    #LINUX
    export http_proxy=""
    export https_proxy=""
    curl -X POST -H "Content-Type: application/json" -d '{"option": "disk", "directory": "/"}' http://localhost:5000/run_script
```

### Listar procesos por uso de cpu

```powershell
    #WINDOWS
    Remove-Item Env:http_proxy
    Remove-Item Env:https_proxy
    curl -X POST -H "Content-Type: application/json" -d '{"option": "cpu"}' http://localhost:5000/run_script
```

```bash
    #LINUX
    export http_proxy=""
    export https_proxy=""
    curl -X POST -H "Content-Type: application/json" -d '{"option": "cpu"}' http://localhost:5000/run_script
```
