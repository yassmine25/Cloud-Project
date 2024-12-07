import logging
from azure.storage.blob import BlobServiceClient
import requests
import json
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Déclenchement de la fonction pour analyser les commentaires.')

    try:
        # Connexion au conteneur Blob Storage (raw-comments)
        connection_string = "DefaultEndpointsProtocol=https;AccountName=commentairesstorage;AccountKey=fQwCvllKcL3YCJ3WAIllddNmkW+2TlHkI8vn/d8/D4U7xaR5VK8L5ihzgN0gC3IfSEy8VxXDygxN+AStKJ6IwQ==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        source_container_name = "raw-comments"
        target_container_name = "processed-comments"
        
        source_container = blob_service_client.get_container_client(source_container_name)
        target_container = blob_service_client.get_container_client(target_container_name)

        # Configuration Azure Cognitive Services Text Analytics
        endpoint = "https://txt-analysis.cognitiveservices.azure.com/"
        subscription_key = "FNrAwdRkYFR3auTg6nB1N18A1vF8N15YZybJgawLwVg5KHlncu3vJQQJ99ALAC5T7U2XJ3w3AAAaACOGmGL2"
        headers = {"Ocp-Apim-Subscription-Key": subscription_key, "Content-Type": "application/json"}

        # Parcourir les blobs dans `raw-comments`
        for blob in source_container.list_blobs():
            blob_client = source_container.get_blob_client(blob.name)
            commentaire_data = blob_client.download_blob().readall()
            commentaire_text = json.loads(commentaire_data)['commentaire']

            # Appel de l'API Text Analytics pour l'analyse de sentiment
            data = {"documents": [{"id": blob.name, "text": commentaire_text}]}
            response = requests.post(f"{endpoint}/text/analytics/v3.0/sentiment", headers=headers, json=data)
            sentiment_result = response.json()

            # Sauvegarder le résultat enrichi dans `processed-comments`
            resultat_nom = f"resultat-{blob.name}"
            resultat_blob_client = target_container.get_blob_client(resultat_nom)
            resultat_blob_client.upload_blob(json.dumps(sentiment_result), overwrite=True)

            logging.info(f"Analyse complétée pour le fichier {blob.name}.")

    except Exception as e:
        logging.error(f"Erreur dans Func_AnalyseCommentaire : {str(e)}")
