import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image
from io import BytesIO
import os

website = 'http://books.toscrape.com/index.html'
URL = ['http://books.toscrape.com/catalogue/category/books/romance_8/index.html', 'http://books.toscrape.com/catalogue/category/books/fiction_10/index.html']
href_livres_in_categorie = []
prefixe_URL = 'http://books.toscrape.com/'


### FONCTIONS

def categorie_du_site (website):
    reponse = requests.get(website)
    soup = BeautifulSoup(reponse.text, 'lxml')
    URL_categorie = []
    for i in soup.find(class_='side_categories').findChild(class_='nav nav-list').find_next('ul').findChildren('a'):
        href_categorie = prefixe_URL + i.get('href')
        URL_categorie.append(href_categorie)
    return(URL_categorie)

# def creation_dataframe_par_categorie(text_categorie):
    nom_categorie = categorie_du_site(text_categorie)
    liste_nom_categorie = nom_categorie[1]
    tableaux = {}
    entete_csv = ('product_page_url', 'universal_ product_code (upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')
    for categorie_tableau in liste_nom_categorie:
        cle_tableau = categorie_tableau
        print(categorie_tableau)
        categorie_tableau =  pd.DataFrame(columns = entete_csv)
        tableaux[cle_tableau] = categorie_tableau
    return(tableaux)

# def remplissage_dataframe(tableaux, liste_livre):
    categorie = liste_livre[-3]
    for i in tableaux :
        if i.keys() == categorie:
            tableaux.loc[len(tableaux)] = liste_livre
        else:
            ()


        print(liste_livre[-3])
        print(tableaux)
        tableaux.loc[len(tableaux)] = liste_livre
        categorie.append(liste_livre[-3])
    else:
        tableaux.loc[len(tableaux)] = liste_livre
    print(categorie)


#Extraction des URL de livres pour une page de catégorie
def listes_livres_par_categorie(URL):
    reponse = requests.get(URL)
    soup = BeautifulSoup(reponse.text, 'lxml')
    for i in soup.find_all(class_='product_pod'):
        for j in i.find_all(class_='image_container'):
            sufixe_URL = j.findChild('a').get('href')
            URL_complet = sufixe_URL.replace("../../..", "http://books.toscrape.com/catalogue")
            href_livres_in_categorie.append(URL_complet)
    return(href_livres_in_categorie)

#Création des pages de catégorie suivants l'index (page 1)
def traitement_pour_plusieurs_pages_par_categorie(URL):
    reponse = requests.get(URL)
    soup = BeautifulSoup(reponse.text, 'lxml')
    nb_page = 0
    new_url = []
    char2 = ''
    if soup.find(class_="pager"):
        text_pager = soup.find(class_='current').get_text()
        char = text_pager.strip()
        char2 = char.replace("Page 1 of ", "")
        nb_page = int(char2)           
    else:                           #essayer de virer le else
        ()
    
    for i in range(1,nb_page):    #struture erreur for i in nb_page:, corrigé
        prefixe_URL = URL.rstrip("index.html")
        sufixe_URL = ("page-"+str(i+1)+".html")
        page_suivante = prefixe_URL + sufixe_URL
        new_url.append(page_suivante)
    return(new_url)

#Extraction des informations pour un livre
def parser_un_livre(URL_livre):                           #ajouter tableau en paramètre ou argument de base none (conditions)
    response_livre = requests.get(URL_livre)
    soup_livre = BeautifulSoup(response_livre.text, 'lxml')
    #Extraction titre OK
    titre = soup_livre.find(class_="col-sm-6 product_main").h1.text
    #Extraction description OK
    descript = soup_livre.find(class_="product_page").findChildren('p')
    description = descript[3].text
    if description == '\n\n\n\n\n\n':
        description = 'Pas de desciption disponible'
    #Extraction catégorie OK
    soup_categorie = soup_livre.find(class_="breadcrumb").findChildren('a')
    categorie = soup_categorie[2].text
    #Extraction de l'image associé
    lien_image_partiel = soup_livre.find(id='product_gallery').findChild(class_='item active').findChild('img').get('src')
    lien_image_complet = lien_image_partiel.replace("../..", prefixe_URL)
    #Extraction info produit
    tds = soup_livre.find(class_="table table-striped").findChildren('td')
    product_information = []
    for i in tds:
        valeur_tds = i.text
        product_information.append(valeur_tds)
    #Extraction de l'image associé
    lien_image_partiel = soup_livre.find(id='product_gallery').findChild(class_='item active').findChild('img').get('src')
    lien_image_complet = lien_image_partiel.replace("../..", prefixe_URL)
    #Enregistrement image de livre
    reponse_image = requests.get(lien_image_complet)
    reponse_image = reponse_image.content
    print(reponse_image)
    img = Image.open(BytesIO(reponse_image))
    if not os.path.exists(f'output/{categorie}'):
        os.makedirs(f'output/{categorie}')
    image = img.save(f'output/{categorie}/{product_information[0]}.jpg')
    #Extraction Star-rating
    class_star = soup_livre.find(class_="instock availability").find_next('p')
    star_review = class_star['class'][1]
    if star_review == 'One':
        review_rating = 1
    elif star_review == 'Two':
        review_rating = 2
    elif star_review == 'Three':
        review_rating = 3
    elif star_review == 'Four':
        review_rating = 4
    elif star_review == 'Five':
        review_rating = 5
    else :
        review_rating = 0
    list_livre = [URL_livre, product_information[0], titre, product_information[2], product_information[3], product_information[5], description, categorie, review_rating, lien_image_complet]
    # creation_dataframe_par_categorie(list_livre)

    return(list_livre)







### CODE PRINCIPAL

entete_csv = ('product_page_url', 'universal_ product_code (upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')
URL_categorie = categorie_du_site(website)
for i in URL_categorie:
    # URL_categorie.append(i)
    URL_complement = traitement_pour_plusieurs_pages_par_categorie(i)
    # print(URL_complement)
    # URL_categorie.append(URL_complement)                          #crée des listes dans la listes, problème
    URL_categorie = URL_categorie + URL_complement
# print(URL_categorie)

for i in URL_categorie:
    href_categorie = listes_livres_par_categorie(i)

tableau = pd.DataFrame(columns = entete_csv)
for i in href_categorie:
    liste_livre = parser_un_livre(i)
    tableau.loc[len(tableau)] = liste_livre
    categorie_dossier = liste_livre[-3]
for categorie_dataframe, group in tableau.groupby('category'):
    group.to_csv(f'output/{categorie_dossier}/{categorie_dataframe}.csv', index=None,  sep= ';',  encoding='utf-32')