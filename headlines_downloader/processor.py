import boto3
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

s3 = boto3.client("s3")

def process_headlines(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Descargar el archivo HTML
        response = s3.get_object(Bucket=bucket, Key=key)
        html_content = response['Body'].read().decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extraer periódico y fecha del nombre del archivo
        filename = os.path.basename(key)
        nombre_periodico, fecha = filename.replace('.html', '').split('-')
        year, month, day = fecha.split('-')

        noticias = []

        if nombre_periodico == "eltiempo":
            # Extrae noticias destacadas de El Tiempo
            for article in soup.select("article a[href]"):
                titulo = article.get_text(strip=True)
                enlace = article.get("href")
                if enlace and not enlace.startswith("http"):
                    enlace = "https://www.eltiempo.com" + enlace
                if titulo and enlace:
                    noticias.append(["General", titulo, enlace])

        elif nombre_periodico == "elespectador":
            # Extrae noticias principales y categorías visibles
            for card in soup.select("section article"):
                categoria_tag = card.select_one("span")
                titulo_tag = card.select_one("a[href]")

                categoria = categoria_tag.get_text(strip=True) if categoria_tag else "General"
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""
                enlace = titulo_tag.get("href") if titulo_tag else ""

                if enlace and not enlace.startswith("http"):
                    enlace = "https://www.publimetro.co/" + enlace

                if titulo and enlace:
                    noticias.append([categoria, titulo, enlace])

        # Crear CSV
        csv_content = "categoria,titulo,enlace\n"
        for row in noticias:
            csv_content += ",".join([f'"{cell}"' for cell in row]) + "\n"

        # Guardar en S3 particionado
        new_key = f"headlines/final/periodico={nombre_periodico}/year={year}/month={month}/day={day}/noticias.csv"
        s3.put_object(Bucket=bucket, Key=new_key, Body=csv_content.encode('utf-8'), ContentType='text/csv')

    return {"message": "Noticias procesadas y guardadas en CSV"}
