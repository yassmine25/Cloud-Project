import azure.storage.blob as blob_module
import json
from datetime import datetime
import azure.functions as func

def main(req):
    # Récupérer les données du commentaire de la requête
    req_body = req.get_json()
    commentaire = req_body.get('commentaire')

    if not commentaire:
        return func.HttpResponse("Commentaire requis", status_code=400)

    # Stocker le commentaire dans Blob Storage
    compte_storage = "commentairesstorage"
    clé_connexion = "fQwCvllKcL3YCJ3WAIllddNmkW+2TlHkI8vn/d8/D4U7xaR5VK8L5ihzgN0gC3IfSEy8VxXDygxN+AStKJ6IwQ=="
    blob_client = blob_module.ContainerClient.from_connection_string(clé_connexion, "raw-comments")

    # Ajoutez le commentaire au Blob sous un format JSON
    nom_fichier = f"commentaire-{datetime.now().isoformat()}.json"
    blob_client.upload_blob(nom_fichier, json.dumps({"commentaire": commentaire}))

    return func.HttpResponse(f"Commentaire reçu !", status_code=200)
