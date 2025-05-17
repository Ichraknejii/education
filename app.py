from flask import Flask, request, jsonify
from flask_cors import CORS
from mistralai import Mistral
import requests
import random

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis Angular

# ------------ CONFIGURATION API ------------
mistral_client = Mistral(api_key="QNq9GtdkKIsY4mYbnISL58VHb91q8hxq")
model_name = "mistral-large-latest"
youtube_key = "AIzaSyDPqg1RYpbPH0K3xRoDlJ5pflcNskAYnlE"

themes = [
    "suite numérique racine de 2",
    "algorithme de recherche dichotomique",
    "tri insertion tri rapide",
    "récursivité vs itératif",
    "analyse de complexité des algorithmes"
]

# ------------ ROUTE : Génération d'une question ------------
@app.route('/api/question', methods=['GET'])
def generer_question():
    theme = random.choice(themes)
    prompt = f"Générez uniquement l'énoncé d'une question Bac Tunisien sur le thème suivant : {theme}. Ne donnez pas la réponse, ni d'explication."
    
    response = mistral_client.chat.complete(
        model=model_name,
        messages=[
            {"role": "system", "content": "Vous êtes un expert du Bac Tunisien."},
            {"role": "user", "content": prompt}
        ]
    )
    return jsonify({
        "theme": theme,
        "question": response.choices[0].message.content.strip() 
    })


# ------------ ROUTE : Correction de la réponse de l'élève ------------
@app.route('/api/correction', methods=['POST'])
def corriger_reponse():
    data = request.get_json()
    question = data['question']
    reponse_eleve = data['reponse']

    reponse_correcte = mistral_client.chat.complete(
        model=model_name,
        messages=[
            {"role": "system", "content": "Vous êtes un correcteur du Bac Tunisien."},
            {"role": "user", "content": f"Question : {question}\nDonnez la bonne réponse avec explication concise."}
        ]
    ).choices[0].message.content.strip()

    correction = mistral_client.chat.complete(
        model=model_name,
        messages=[
            {"role": "system", "content": "Corrigez la réponse d'un élève."},
            {"role": "user", "content": f"Question : {question}\nRéponse élève : {reponse_eleve}\nBonne réponse : {reponse_correcte}"}
        ]
    ).choices[0].message.content.strip()

    return jsonify({
        "bonne_reponse": reponse_correcte,
        "correction": correction
    })


# ------------ ROUTE : Recommandation de vidéo YouTube ------------
@app.route('/api/video', methods=['GET'])
def recommander_video():
    theme = request.args.get("theme", random.choice(themes))
    params = {
        'part': 'snippet',
        'q': theme,
        'type': 'video',
        'maxResults': 1,
        'key': youtube_key
    }
    yt_response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)

    if yt_response.status_code != 200:
        return jsonify({"error": "Erreur API YouTube"}), 500

    items = yt_response.json().get('items', [])
    if not items:
        return jsonify({"error": "Aucune vidéo trouvée"}), 404

    video = items[0]
    title = video['snippet']['title']
    video_id = video['id']['videoId']
    url = f"https://www.youtube.com/watch?v={video_id}"

    return jsonify({"titre": title, "url": url})

# ------------ LANCEMENT FLASK ------------
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)  
