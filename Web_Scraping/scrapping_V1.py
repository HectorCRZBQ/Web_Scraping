import requests
from bs4 import BeautifulSoup

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

    # Itera a través de los enlaces a las noticias
    for enlace in enlaces_noticias:
        # Realiza una solicitud GET para obtener el contenido de la noticia
        noticia_response = requests.get(enlace)
        if noticia_response.status_code == 200:
            # Parsea el contenido HTML de la noticia
            noticia_soup = BeautifulSoup(noticia_response.text, 'html.parser')
            
            # Encuentra todos los párrafos dentro del contenido de la noticia
            parrafos = noticia_soup.find_all('p')
            
            # Itera a través de los párrafos y muestra su contenido
            for parrafo in parrafos:
                contenido_parrafo = parrafo.get_text()
                print(contenido_parrafo)
        else:
            print(f'No se pudo acceder a la noticia: {enlace}')
else:
    print('No se pudo acceder a la página web.')