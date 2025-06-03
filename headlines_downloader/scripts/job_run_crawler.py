import boto3

def run_crawler(event=None, context=None):
    glue = boto3.client("glue")
    
    crawler_name = "crawler_headlines_final"  

    try:
        glue.start_crawler(Name=crawler_name)
        print(f"✅ Crawler '{crawler_name}' iniciado correctamente.")
        return {"message": "Crawler iniciado"}
    
    except glue.exceptions.CrawlerRunningException:
        print(f"⚠️ El crawler '{crawler_name}' ya está en ejecución.")
        return {"message": "Crawler ya en ejecución"}
    
    except Exception as e:
        print(f"❌ Error al iniciar el crawler: {e}")
        return {"error": str(e)}
