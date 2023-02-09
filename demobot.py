from PIL import Image, ImageDraw, ImageFont

import requests
import json
import csv
import io

from dotenv import dotenv_values
config = dotenv_values(".env")

def wrap_text(text, width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        if len(line) + len(word) <= width:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    return lines

def read_phrases_from_file(filename):
    phrases = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            phrases.append(row[0])
    return phrases

def generate_text_image(text):
    # définir la taille de l'image
    width, height = 512, 512

    # créer une image blanche
    image = Image.new("RGB", (width, height), (255, 255, 255))

    # définir la police et la taille du texte
    font = ImageFont.truetype("fonts/Original-Bold.ttf", 36)

    # créer un objet dessin pour écrire sur l'image
    draw = ImageDraw.Draw(image)

    # obtenir les coordonnées pour centrer le texte sur l'image
    text_width, text_height = draw.textsize(text, font)
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2

    # écrire le texte sur l'image
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))

    return image

def search_image(query):
    # définir l'URL de l'API Unsplash
    #url = "https://api.unsplash.com/search/photos?query={}&client_id={}".format(query, os.getenv("CLIENT_ID"))
    # définir l'URL de l'API Unsplash avec le dotenv
    url = "https://api.unsplash.com/search/photos?query={}&client_id={}".format(query, config["CLIENT_ID"])

    # faire une requête à l'API
    response = requests.get(url)

    # vérifier que la requête a réussi
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        # obtenir le lien de l'image trouvée
        image_url = data["results"][0]["urls"]["regular"]

        # télécharger l'image
        image = requests.get(image_url).content

        # mettre l'image dans un objet Image
        image = Image.open(io.BytesIO(image))

        return image
    else:
        print("Erreur lors de la requête à l'API Unsplash")
        return None
    
def save_image(image, filename):
    image.save(filename, "JPEG")


# for dev purposes
# del all images in folder img/
import os
for filename in os.listdir("img"):
    os.remove("img/" + filename)
for filename in os.listdir("themes"):
    os.remove("themes/" + filename)

phrases = read_phrases_from_file("phrases_test.csv")
for i, phrase in enumerate(phrases):
    # générer une image avec le texte

    phrase = wrap_text(phrase, 20) # ceci retourne une liste de lignes
    phrase = "\n".join(phrase) # ceci transforme la liste en une chaîne de caractères
    text_image = generate_text_image(phrase)

    # trouver une image correspondant au thème de la phrase
    theme = "apple"
    theme_image = search_image(theme)

    # enregistrer l'image sur le disque dur
    save_image(text_image, "img/text_image_{}.jpeg".format(i))
    save_image(theme_image, "themes/theme_image_{}.jpeg".format(i))