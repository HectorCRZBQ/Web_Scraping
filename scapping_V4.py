import tkinter as tk
from tkinter import scrolledtext
from bs4 import BeautifulSoup as bs
import requests
import re
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import spacy
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import threading

class Scrapping:
    def __init__(self):
        self.url = 'https://www.marca.com'
        self.clase_objetivo = 'ue-c-cover-content__link'

        self.ventana = tk.Tk()
        self.ventana.title("Web Scraping")

        self.etiqueta = tk.Label(self.ventana, text="Búsqueda en www.marca.com")
        self.etiqueta.pack()

        self.etiqueta = tk.Label(self.ventana, text="Posibles búsquedas: futbol, tenis, coches, ciclismo y baloncesto")
        self.etiqueta.pack()

        self.etiqueta_palabras_clave = tk.Label(self.ventana, text="Palabras Clave:")
        self.etiqueta_palabras_clave.pack()
        self.entrada_palabras_clave = tk.Entry(self.ventana)
        self.entrada_palabras_clave.pack()

        self.boton_mostrar_texto = tk.Button(self.ventana, text="Mostrar Texto del Enlace", command=self.mostrar_texto_enlace)
        self.boton_mostrar_texto.pack()
        self.boton_mostrar_texto.config(state=tk.DISABLED)

        self.boton_buscar = tk.Button(self.ventana, text="Buscar", command=self.buscar_palabras_clave)
        self.boton_buscar.pack()

        self.boton_cerrar = tk.Button(self.ventana, text="Cerrar", command=self.ventana.destroy)
        self.boton_cerrar.pack()

        self.grafico_frame = tk.Frame(self.ventana)
        self.grafico_frame.pack()

        self.resultado_label = tk.Label(self.ventana, text="")
        self.resultado_label.pack()

        self.error_label = tk.Label(self.ventana, text="", fg="red")
        self.error_label.pack()

        self.entrada_palabras_clave.bind('<Return>', self.buscar_palabras_clave)

        self.link_text = None  # Variable para almacenar el texto de los enlaces
        self.noticias_encontradas = []
        self.nlp = spacy.load("es_core_news_sm")
        self.enlaces_encontrados = []
        self.palabras_filtradas = set()
        self.palabras_comunes = Counter()

    def iniciar(self):
        self.ventana.mainloop()

    def es_palabra_filtrada(self, token):
        # Agrega aquí tu lógica para filtrar palabras, por ejemplo, palabras vacías (stop words)
        palabras_filtradas = ["a", "de", "en", "el", "la", "y", "que"]  # Ejemplo de palabras filtradas
        return token.text.lower() in palabras_filtradas

    def buscar_palabras_clave(self, event=None):
        keyword = self.entrada_palabras_clave.get().lower()  # Convertir a minúsculas
        expresion_palabras_clave = r'\b(futbol|tenis|coches|baloncesto|ciclismo)\b'

        if not re.search(expresion_palabras_clave, keyword):
            self.resultado_label.config(text="La entrada no coincide con ninguna de las opciones.")
            return

        # Cambiar el encabezado de la solicitud para parecer un navegador web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        try:
            response = requests.get(self.url, headers=headers)

            if response.status_code == 200:
                soup = bs(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                contador = Counter()

                # Utilizar ThreadPoolExecutor para procesar enlaces en paralelo
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    for link in links:
                        link_url = link['href']

                        # Verificar si la URL contiene la palabra clave
                        if re.search(expresion_palabras_clave, link_url):
                            futures.append(executor.submit(self.procesar_enlace, link_url, keyword))

                    # Esperar a que todas las tareas se completen
                    concurrent.futures.wait(futures)

                    # Recopilar resultados
                    for future in futures:
                        result = future.result()
                        if result:
                            self.enlaces_encontrados.append(result)

                if not self.enlaces_encontrados:
                    self.resultado_label.config(text="No se encontraron enlaces en la ruta relativa " + keyword)
                    return

                # Mostrar el mensaje de la ruta relativa encontrada
                self.resultado_label.config(text="Ruta relativa encontrada: " + keyword)

                # Restablecer la lista de noticias encontradas al inicio de la búsqueda
                self.noticias_encontradas = []

                # Restablecer la lista de palabras comunes
                self.palabras_comunes = Counter()

                # Procesar las noticias y filtrar palabras
                for enlace_encontrado in self.enlaces_encontrados:
                    contenido_parrafo = enlace_encontrado['texto']
                    # Tokeniza el contenido del párrafo utilizando spaCy
                    doc = self.nlp(contenido_parrafo)
                    # Filtra las palabras que no son palabras vacías (stop words) ni verbos
                    palabras_filtradas = [token.text.lower() for token in doc if not self.es_palabra_filtrada(token)]
                    self.palabras_filtradas.update(palabras_filtradas)
                    self.palabras_comunes.update(palabras_filtradas)

                # Mostrar las palabras clave encontradas en las noticias de la ruta relativa
                top_palabras = self.palabras_comunes.most_common(10)

                palabras, counts = zip(*top_palabras)

                self.entrada_palabras_clave.delete(0, tk.END)

                for widget in self.grafico_frame.winfo_children():
                    widget.destroy()

                figura = Figure(figsize=(6, 4), dpi=100)
                subplot = figura.add_subplot(111)
                subplot.barh(palabras, counts)
                subplot.set_xlabel('Cantidad de Apariciones')
                subplot.set_ylabel('Palabra')
                subplot.set_title('Palabras Más Comunes')

                canvas = FigureCanvasTkAgg(figura, master=self.grafico_frame)
                canvas.get_tk_widget().pack()
                canvas.draw()

                self.boton_mostrar_texto.config(state=tk.NORMAL)  # Habilitar el botón para mostrar texto de enlace

            else:
                self.error_label.config(text="Ocurrió un error al intentar obtener los datos.")

        except Exception as e:
            self.error_label.config(text="Ocurrió un error al intentar obtener los datos: " + str(e))

    def mostrar_texto_enlace(self):
        try:
            if not self.enlaces_encontrados:
                self.error_label.config(text="No hay enlaces para mostrar.")
                return

            # Crear una nueva ventana emergente para mostrar el texto del enlace
            ventana_emergente = tk.Toplevel(self.ventana)
            ventana_emergente.title("Texto del Enlace")

            # Crear una cadena para almacenar el texto de los enlaces
            texto_enlaces = ""
            for noticia in self.enlaces_encontrados:
                texto_enlaces += f"URL: {noticia['url']}\nTexto: {noticia['texto']}\n\n"

            # Agregar un área de texto desplazable para mostrar el texto del enlace
            texto_desplazable = scrolledtext.ScrolledText(ventana_emergente, wrap=tk.WORD, width=60, height=20)
            texto_desplazable.insert(tk.INSERT, texto_enlaces)
            texto_desplazable.pack()

        except Exception as e:
            print("Error mostrando texto del enlace", e)

    def procesar_enlace(self, link_url, keyword):
        try:
            enlace_completo = urljoin(self.url, link_url)
            noticia_response = requests.get(enlace_completo)
            noticia_response.raise_for_status()  # Maneja errores HTTP

            # Parsea el contenido HTML de la noticia
            noticia_soup = bs(noticia_response.text, 'html.parser')

            # Encuentra todos los párrafos dentro del contenido de la noticia
            parrafos = noticia_soup.find_all('p')

            # Itera a través de los párrafos y filtra palabras
            for parrafo in parrafos:
                contenido_parrafo = parrafo.get_text()
                if re.search(keyword, contenido_parrafo, re.IGNORECASE):
                    return {'url': enlace_completo, 'texto': contenido_parrafo}

        except Exception as e:
            print("Error al procesar enlace:", e)
        return None

if __name__ == '__main__':
    app = Scrapping()
    app.iniciar()