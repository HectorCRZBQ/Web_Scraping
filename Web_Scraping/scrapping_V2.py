import requests
from bs4 import BeautifulSoup

# URL de la página web que deseas analizar
url = 'https://www.marca.com/coches-y-motos/coches.html'

# Realiza la solicitud GET para obtener el contenido de la página web principal
response = requests.get(url)

# Verifica si la solicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Parsea el contenido HTML de la página web usando Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encuentra todos los enlaces a las subpáginas de noticias
    links = soup.find_all('a', class_='enlace-mas')
    
    # Itera a través de los enlaces y accede a cada subpágina
    for link in links:
        subpage_url = link['href']
        
        # Verifica si la URL es válida y está completa
        if not subpage_url.startswith('http'):
            subpage_url = 'https://www.marca.com' + subpage_url

        subpage_response = requests.get(subpage_url)
        
        # Verifica si la solicitud a la subpágina fue exitosa (código de estado 200)
        if subpage_response.status_code == 200:
            # Parsea el contenido HTML de la subpágina
            subpage_soup = BeautifulSoup(subpage_response.text, 'html.parser')
            
            # Encuentra el elemento que contiene el texto completo (ajusta esto según la estructura real)
            article_content = subpage_soup.find('div', class_='noticia')
            
            if article_content:
                # Extrae el texto completo de la subpágina
                subpage_text = article_content.get_text()
                
                # Imprime el texto completo de la subpágina
                print(subpage_text)
            else:
                print(f'No se encontró contenido en la subpágina: {subpage_url}')
        else:
            print(f'No se pudo acceder a la subpágina: {subpage_url}')
else:
    print('No se pudo acceder a la página web principal.')