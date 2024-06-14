import openai
import json
from settings import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY


def analyser_texte_juridique(texte):
    """
    Analyse un texte juridique en utilisant ChatGPT et extrait les informations clés.
    
    :param texte: Le texte juridique à analyser.
    :return: Dictionnaire JSON des informations extraites.
    """
    # Envoie le texte à ChatGPT pour analyse
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=f"Analyser le texte suivant pour extraire les informations clés d'un procès-verbal d'assemblée générale : {texte}",
        max_tokens=1024
    )

    # Obtention des informations extraites par ChatGPT
    extracted_data = response.choices[0].text.strip()

    # Conversion des informations extraites en format JSON
    try:
        # Tentative de conversion en format JSON si la réponse est déjà bien structurée
        json_data = json.loads(extracted_data)
    except json.JSONDecodeError:
        # Création manuelle du JSON si la sortie n'est pas déjà en JSON
        json_data = {
            "error": "La sortie n'est pas en format JSON valide, nécessite une vérification manuelle",
            "raw_output": extracted_data
        }

    return json_data

# # Texte d'exemple (devrait être remplacé par un vrai texte juridique)
# texte_exemple = """
# Procès-verbal de l'assemblée générale du 25 mars 2021
# Ordre du jour: Élection du conseil d'administration, Approbation des comptes annuels, Divers.
# Participants: Jean Dupont - Président, Marie Curie - Trésorière.
# """

# # Analyse du texte
# informations = analyser_texte_juridique(texte_exemple)

# # Affichage des informations extraites
# print(json.dumps(informations, indent=4))
