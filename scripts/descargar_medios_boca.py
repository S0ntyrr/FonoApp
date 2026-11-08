"""Descarga legal opcional de demos HUMANAS a la carpeta estática de FonoApp.

No modifica MongoDB, audio de pacientes ni código; conserva atribuciones.
Ejecución: python scripts/descargar_medios_boca.py
Los enlaces corresponden a Wikimedia Commons CC BY-SA 4.0.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

DIR = Path(__file__).resolve().parents[1] / 'app' / 'static' / 'media' / 'fonemas'
MEDIOS = {
    'rr.webm': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Alveolar-trill-slomo.webm',
    'lectura-labial-general.gif': 'https://upload.wikimedia.org/wikipedia/commons/d/d3/LipReading.gif',
}

def main():
    DIR.mkdir(parents=True, exist_ok=True)
    for nombre, url in MEDIOS.items():
        archivo = DIR / nombre
        if archivo.is_file() and archivo.stat().st_size > 2000:
            print('YA EXISTE:', nombre)
            continue
        print('Descargando:', nombre)
        try:
            with urlopen(Request(url, headers={'User-Agent':'FonoAppEducational/1.0 (licensed media download; contact via source Wikimedia Commons)'}), timeout=25) as src, archivo.open('wb') as out:
                total = 0
                while parte := src.read(256 * 1024):
                    total += len(parte)
                    if total > 10 * 1024 * 1024:
                        raise ValueError('Archivo inesperadamente grande')
                    out.write(parte)
            print('OK:', archivo, 'bytes:', archivo.stat().st_size)
        except (URLError, OSError, ValueError) as exc:
            archivo.unlink(missing_ok=True)
            print('SIN DESCARGAR:', nombre, '-', str(exc))
    print('Licencias y atribuciones: DOCUMENTACION_MEDIOS_REALES.md')

if __name__ == '__main__':
    main()
