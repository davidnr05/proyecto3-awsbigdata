import requests
import boto3
from bs4 import BeautifulSoup
from datetime import datetime
#rr
def scrape_headlines(event=None, context=None):
    urls = {
        "eltiempo": "https://www.eltiempo.com/",
        "publimetro": "https://www.publimetro.co/"
    }

    s3 = boto3.client("s3")
    bucket = "headlinesjune"  # ← Estaba mal cerrada la comilla
    today = datetime.utcnow().strftime("%Y-%m-%d")
    year, month, day = today.split("-")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    for nombre, url in urls.items():
        # 1. Descargar HTML
        response = requests.get(url, headers=headers, timeout=10)
        html = response.content.decode("utf-8")

        # 2. Guardar HTML en S3
        raw_key = f"headlines/raw/{nombre}-{today}.html"
        s3.put_object(
            Bucket=bucket,
            Key=raw_key,
            Body=response.content,
            ContentType='text/html'
        )

        # 3. Procesar con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        noticias = []

        if nombre == "eltiempo":
            for a in soup.select("article a[href]"):
                titulo = a.get_text(strip=True)
                enlace = a.get("href")
                if enlace and not enlace.startswith("http"):
                    enlace = "https://www.eltiempo.com" + enlace
                if titulo and enlace:
                    noticias.append(["General", titulo, enlace])

        elif nombre == "publimetro":
            for link in soup.select("a[href]"):
                titulo = link.get_text(strip=True)
                enlace = link.get("href")
                if enlace and titulo and "/" in enlace and len(titulo) > 40:
                    if not enlace.startswith("http"):
                        enlace = "https://www.publimetro.co" + enlace
                    noticias.append(["General", titulo, enlace])

        # 4. Crear CSV en memoria
        csv = "categoria,titulo,enlace\n"
        for row in noticias:
            csv += ",".join(f'"{r}"' for r in row) + "\n"

        # 5. Guardar CSV en S3
        final_key = f"headlines/final/periodico={nombre}/year={year}/month={month}/day={day}/noticias.csv"
        s3.put_object(
            Bucket=bucket,
            Key=final_key,
            Body=csv.encode("utf-8"),
            ContentType="text/csv"
        )

    return {"message": "HTML descargados y procesados correctamente"}
