import requests
import boto3
from datetime import datetime

def scrape_headlines(event, context):
    urls = {
        "eltiempo": "https://www.eltiempo.com/",
        "elespectador": "https://www.elespectador.com/"
    }

    s3 = boto3.client("s3")
    bucket = "headlinesjune"  # Cambia esto por el bucket real
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for nombre, url in urls.items():
        response = requests.get(url, timeout=10)
        filename = f"headlines/raw/{nombre}-{today}.html"
        s3.put_object(
            Bucket=bucket,
            Key=filename,
            Body=response.content,
            ContentType='text/html'
        )

    return {"message": "Páginas guardadas exitosamente."}
