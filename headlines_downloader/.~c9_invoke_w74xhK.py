import requests
import boto3
from datetime import datetime

def scrape_headlines(event=None, context=None):
    urls = {
        "eltiempo": "https://www.eltiempo.com/",
        "elespectador": "https://www.elespectador.com/"
    }

    s3 = boto3.client("s3")
    bucket = "headlinesjune"
    today = datetime.utcnow().strftime("%Y-%m-%d")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    ),
        
        
    }

    for nombre, url in urls.items():
        response = requests.get(url, headers=headers, timeout=10)
        filename = f"headlines/raw/{nombre}-{today}.html"
        s3.put_object(
            Bucket=bucket,
            Key=filename,
            Body=response.content,
            ContentType='text/html'
        )

    return {"message": "Páginas descargadas correctamente"}
