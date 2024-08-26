import requests
import os

URL = 'https://eval-s3-py-script.s3.amazonaws.com/script.sh'  # URL de donde se descargará el script
LOCAL_SCRIPT_PATH = '/app/script.sh'
TEMP_SCRIPT_PATH = '/app/temp_script.sh'

def download_script(url, path):
    """Descargar el script desde la URL y guardarlo en el path especificado."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as file:
            file.write(response.content)
        print(f'Script descargado exitosamente desde {url}')
        return True
    except requests.exceptions.RequestException as e:
        print(f'Error al descargar el script: {e}')
        return False

def check_for_update():
    """Verificar si hay una nueva versión del script y descargarla si es necesario."""
    # Descargar el script temporalmente
    if download_script(URL, TEMP_SCRIPT_PATH):
        # Comparar con el script actual
        if os.path.exists(LOCAL_SCRIPT_PATH):
            with open(LOCAL_SCRIPT_PATH, 'rb') as local_file:
                local_content = local_file.read()
            with open(TEMP_SCRIPT_PATH, 'rb') as temp_file:
                temp_content = temp_file.read()
            # Si los contenidos son diferentes, reemplazar el script actual
            if local_content != temp_content:
                os.replace(TEMP_SCRIPT_PATH, LOCAL_SCRIPT_PATH)
                print('Nueva versión del script detectada y actualizada.')
            else:
                print('No hay nueva versión del script disponible.')
                os.remove(TEMP_SCRIPT_PATH)
        else:
            # Si el script local no existe, simplemente renombrar el temporal
            os.rename(TEMP_SCRIPT_PATH, LOCAL_SCRIPT_PATH)
            print('Script descargado por primera vez.')

if __name__ == '__main__':
    check_for_update()