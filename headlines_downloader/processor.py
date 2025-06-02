import boto3
import os
from bs4 import BeautifulSoup
from datetime import datetime

s3 = boto3.client("s3")

def process_headlines(event, context):
    print("🔁 Lambda processor.process_headlines activado")

    keys = []

    # Si se invoca con evento S3
    if event and 'Records' in event:
        for record in event['Records']:
            keys.append(record['s3']['object']['key'])

    # Si se invoca manualmente (por app.py o prueba)
    elif event and 'keys' in event:
        keys = event['keys']
    
    else:
        print("⚠️ No se proporcionaron claves para procesar")
        return {"message": "No hay archivos para procesar"}

    for key in keys:
        bucket = "headlinesjune"  # Reemplaza por tu bucket si lo necesitas estático

        if not key.endswith('.html'):
            continue

        # Descargar archivo HTML
        response = s3.get_object(Bucket=bucket, Key=key)
        html = response['Body'].read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Extraer nombre del periódico y fecha
        filename = os.path.basename(key)
        nombre_periodico, fecha = filename.replace('.html', '').split('-')
        year, month, day = fecha.split('-')

        noticias = []

        if nombre_periodico == "eltiempo":
            for article in soup.select("article a[href]"):
                titulo = article.get_text(strip=True)
                enlace = article.get("href")
                if enlace and not enlace.startswith("http"):
                    enlace = "https://www.eltiempo.com" + enlace
                if titulo and enlace:
                    noticias.append(["General", titulo, enlace])

        elif nombre_periodico == "publimetro":
            for link in soup.select("a[href]"):
                titulo = link.get_text(strip=True)
                enlace = link.get("href")
                if enlace and titulo and "/" in enlace and len(titulo) > 40:
                    if not enlace.startswith("http"):
                        enlace = "https://www.publimetro.co" + enlace
                    noticias.append(["General", titulo, enlace])

        # Crear CSV en memoria
        csv = "categoria,titulo,enlace\n"
        for row in noticias:
            csv += ",".join(f'"{r}"' for r in row) + "\n"

        # Guardar CSV en S3 particionado
        key_csv = f"headlines/final/periodico={nombre_periodico}/year={year}/month={month}/day={day}/noticias.csv"
        s3.put_object(
            Bucket=bucket,
            Key=key_csv,
            Body=csv.encode("utf-8"),
            ContentType="text/csv"
        )

    return {"message": "Procesamiento y guardado de noticias completado"}
