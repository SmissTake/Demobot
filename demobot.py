import random
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

def get_theme_for_phrase(phrase, filename):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == phrase:
                return row[1]
    return ""

def get_image_color(image_path):
    # Ouvrir l'image en utilisant Pillow
    image = Image.open(image_path)

    # Convertir l'image en tableau de pixels
    pixels = image.convert("RGB").getdata()

    # Initialiser des compteurs pour les couleurs R, G et B
    r = 0
    g = 0
    b = 0

    # Pour chaque pixel dans l'image, additionner les valeurs R, G et B
    for pixel in pixels:
        r += pixel[0]
        g += pixel[1]
        b += pixel[2]

    # Diviser les totaux pour les couleurs par le nombre de pixels pour obtenir la couleur moyenne
    average_color = (r / len(pixels), g / len(pixels), b / len(pixels))

    # transforme la couleur moyenne compatible avec la fonction fill de Pillow
    average_color = tuple(int(x) for x in average_color)

    return average_color

# retourne une police aléatoire du dossier fonts
def get_random_font():
    fonts = os.listdir("fonts")
    random_font = random.choice(fonts)
    return random_font

def get_complement_color(color):
    # obtenir la couleur complémentaire
    complement_color = (255 - color[0], 255 - color[1], 255 - color[2])

    return complement_color

def generate_text_image(text, themebg):
    # définir la taille de l'image
    width, height = 512, 512

    # créer une image blanche
    image = Image.new("RGB", (width, height), (255, 255, 255))

    # définir la police et la taille du texte
    font = ImageFont.truetype("fonts/{}".format(get_random_font()), 36)

    # créer un objet dessin pour écrire sur l'image
    draw = ImageDraw.Draw(image)

    # obtenir les coordonnées pour centrer le texte sur l'image
    text_width, text_height = draw.textsize(text, font)
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2

    # Charger l'image de fond
    theme_image = Image.open("themes/{}".format(themebg))

    # obtenir la couleur moyenne de l'image de fond
    average_color = get_image_color(theme_image.filename)

    # obtenir la couleur complémentaire de la couleur moyenne
    text_color = get_complement_color(average_color)

    # Redimensionner l'image pour remplir complètement le cadre
    theme_ratio = theme_image.width / theme_image.height
    image_ratio = width / height

    if theme_ratio > image_ratio:
        new_width = int(height * theme_ratio)
        theme_image = theme_image.resize((new_width, height), Image.ANTIALIAS)
        left = (new_width - width) / 2
        right = new_width - left
        top = 0
        bottom = height
        theme_image = theme_image.crop((left, top, right, bottom))
    else:
        new_height = int(width / theme_ratio)
        theme_image = theme_image.resize((width, new_height), Image.ANTIALIAS)
        top = (new_height - height) / 2
        bottom = new_height - top
        left = 0
        right = width
        theme_image = theme_image.crop((left, top, right, bottom))

    # Coller l'image de fond sur l'image principale
    image.paste(theme_image, (0, 0))

    position = (text_x, text_y)

    # dessiner un rectangle autour du texte avec une marge de 10 pixels et la couleur moyenne opacifiée
    draw.rectangle((text_x - 10, text_y - 10, text_x + text_width + 10, text_y + text_height + 10), fill=average_color)
    # écrire le texte sur l'image
    draw.text((text_x, text_y), text, font=font, fill=text_color)

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
# del all images in folder img/ and themes/ except .gitkeep
import os
for filename in os.listdir("img"):
    if filename != ".gitkeep":
        os.remove(os.path.join("img", filename))
for filename in os.listdir("themes"):
    if filename != ".gitkeep":
        os.remove(os.path.join("themes", filename))

phrases = read_phrases_from_file("phrases_test.csv")
for i, phrase in enumerate(phrases):
    # générer une image avec le texte

    # trouver une image correspondant au thème de la phrase
    theme = get_theme_for_phrase(phrase, "phrases_test.csv")
    theme_image = search_image(theme)
    save_image(theme_image, "themes/theme_image_{}.jpeg".format(i))

    phrase = wrap_text(phrase, 20) # ceci retourne une liste de lignes
    phrase = "\n".join(phrase) # ceci transforme la liste en une chaîne de caractères
    text_image = generate_text_image(phrase, "theme_image_{}.jpeg".format(i))

    # enregistrer l'image sur le disque dur
    save_image(text_image, "img/text_image_{}.jpeg".format(i))