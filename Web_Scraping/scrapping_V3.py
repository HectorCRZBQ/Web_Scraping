import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import spacy
from urllib.parse import urlparse

# Cargar el modelo de spaCy para el español
nlp = spacy.load("es_core_news_sm")

# URL de la página web que deseas analizar
url = 'https://www.marca.com/coches-y-motos/coches.html'

# Clase específica que quieres encontrar (en este caso, los enlaces a las noticias)
clase_objetivo = 'ue-c-cover-content__link'

# Realiza la solicitud GET para obtener el contenido de la página web
response = requests.get(url)

# Verifica si la solicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Parsea el contenido HTML de la página web usando Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra todos los elementos con la clase específica (enlaces a las noticias)
    enlaces_noticias = [elemento.get('href') for elemento in soup.find_all(class_=clase_objetivo)]

    # Crear un contador de palabras
    word_counter = Counter()

    # Crear un diccionario para almacenar los enlaces correspondientes a cada palabra
    enlaces_dict = {}

    # Itera a través de los enlaces a las noticias
    for enlace in enlaces_noticias:
        # Realiza una solicitud GET para obtener el contenido de la noticia
        noticia_response = requests.get(enlace)
        if noticia_response.status_code == 200:
            # Parsea el contenido HTML de la noticia
            noticia_soup = BeautifulSoup(noticia_response.text, 'html.parser')
            
            # Encuentra todos los párrafos dentro del contenido de la noticia
            parrafos = noticia_soup.find_all('p')
            
            # Itera a través de los párrafos y elimina palabras vacías y otros tipos de palabras
            for parrafo in parrafos:
                contenido_parrafo = parrafo.get_text()
                # Tokeniza el contenido del párrafo utilizando spaCy
                doc = nlp(contenido_parrafo)
                # Filtra las palabras que no son palabras vacías (stop words) ni verbos
                palabras_filtradas = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_digit]
                word_counter.update(palabras_filtradas)
                
                # Actualiza el diccionario de enlaces con el enlace correspondiente a cada palabra
                for palabra in palabras_filtradas:
                    if palabra in enlaces_dict:
                        enlaces_dict[palabra].append(enlace)
                    else:
                        enlaces_dict[palabra] = [enlace]
        else:
            print(f'No se pudo acceder a la noticia: {enlace}')

    # Obtener las palabras y sus frecuencias ordenadas por frecuencia descendente
    palabras_frecuencia_descendente = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)

    # Limitar a las 20 palabras más frecuentes
    top_n = 20
    palabras_ordenadas = [item[0] for item in palabras_frecuencia_descendente[:top_n]]
    frecuencias_ordenadas = [item[1] for item in palabras_frecuencia_descendente[:top_n]]

    # Crear una disposición de subgráficos con Matplotlib
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Mostrar el gráfico de pastel en el primer subgráfico
    ax1.pie(frecuencias_ordenadas, labels=palabras_ordenadas, autopct='%1.1f%%', startangle=140)
    ax1.set_title('Distribución de Palabras Más Frecuentes en los Párrafos de las Noticias')
    ax1.axis('equal')  # Para asegurarse de que el gráfico de pastel sea un círculo

    # Obtener las 10 palabras más frecuentes detrás de la palabra más frecuente en el gráfico circular
    palabra_mas_frecuente = palabras_ordenadas[0]
    palabras_detras_mas_frecuente = [item[0] for item in palabras_frecuencia_descendente[1:11]]

    # Recortar los enlaces para mostrar solo el dominio en la tabla
    enlaces_recortados = [urlparse(enlace).netloc for enlace in enlaces_dict[palabra_mas_frecuente][:10]]

    # Crear un DataFrame para mostrar la información en el segundo subgráfico
    data = {
        'Palabra': palabras_detras_mas_frecuente,
        'Frecuencia': [word_counter[palabra] for palabra in palabras_detras_mas_frecuente],
        'Enlaces': enlaces_recortados
    }
    df = pd.DataFrame(data)

    # Mostrar la tabla en el segundo subgráfico
    ax2.axis('off')  # Ocultar los ejes
    table = ax2.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)  # Ajustar el tamaño de la tabla

    plt.show()

else:
    print('No se pudo acceder a la página web.')