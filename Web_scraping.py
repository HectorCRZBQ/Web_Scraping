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
from unidecode import unidecode

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

        self.boton_cerrar = tk.Button(self.ventana, text="Cerrar", command=self.ventana.quit)
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

    def buscar_palabras_clave(self, event=None):
        keyword = self.entrada_palabras_clave.get()
        expresion_palabras_clave = r'\b(futbol|tenis|coches|baloncesto|ciclismo)\b'

        if not re.search(expresion_palabras_clave, keyword):
            self.resultado_label.config(text="La entrada no coincide con ninguna de las opciones.")
            return

        def procesar_enlace(link):
            try:
                link_url = link['href']
                link_text = link.get_text()

                if re.search(keyword, link_url):
                    enlace_completo = urljoin(self.url, link_url)

                    noticia_response = requests.get(enlace_completo)
                    noticia_response.raise_for_status()

                    noticia_soup = bs(noticia_response.text, 'html.parser')
                    parrafos = noticia_soup.find_all('p')

                    palabras_filtradas = self.filtrar_palabras(parrafos)
                    self.palabras_comunes.update(palabras_filtradas)

                    # Almacena el texto y la URL del enlace
                    self.enlaces_encontrados.append({'url': enlace_completo, 'texto': link_text})

            except Exception as e:
                print("Error procesando enlace:", e)

        # Cambiar el encabezado de la solicitud para parecer un navegador web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        try:
            response = requests.get(self.url, headers=headers)

            if response.status_code == 200:
                soup = bs(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                with ThreadPoolExecutor(max_workers=10000) as executor:
                    executor.map(procesar_enlace, links)

                if not self.palabras_comunes:
                    self.resultado_label.config(text="No se encontraron enlaces en la ruta relativa " + keyword)
                    return

                self.resultado_label.config(text="Ruta relativa encontrada: " + keyword)

                self.mostrar_grafico_palabras_comunes()

                self.boton_mostrar_texto.config(state=tk.NORMAL)

            else:
                self.error_label.config(text="Ocurrió un error al intentar obtener los datos.")

        except Exception as e:
            self.error_label.config(text="Ocurrió un error al intentar obtener los datos: " + str(e))

    def filtrar_palabras(self, parrafos):
            palabras_filtradas = set()
            for parrafo in parrafos:
                contenido_parrafo = parrafo.get_text()
                doc = self.nlp(contenido_parrafo)

                # Filtrar y agregar solo palabras
                palabras_filtradas.update(
                    unidecode(token.text.lower())  # Convierte a ASCII y hace minúsculas
                    for token in doc
                    if not self.es_palabra_filtrada(token)
                )

            return palabras_filtradas

    def es_palabra_filtrada(self, token):
        return token.is_stop or token.is_punct or token.is_digit

    def mostrar_grafico_palabras_comunes(self):
        top_palabras = self.palabras_comunes.most_common(10)
        palabras, counts = zip(*top_palabras)

        self.entrada_palabras_clave.delete(0, tk.END)

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        figura = Figure(figsize=(8, 6), dpi=100)
        subplot = figura.add_subplot(111)
        subplot.barh(palabras, counts)
        subplot.set_xlabel('Cantidad de Apariciones')
        subplot.set_ylabel('Palabra')
        subplot.set_title('Palabras Más Comunes')

        canvas = FigureCanvasTkAgg(figura, master=self.grafico_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def mostrar_texto_enlace(self):
        try:
            if not self.enlaces_encontrados:
                self.error_label.config(text="No hay enlaces para mostrar.")
                return

            ventana_emergente = tk.Toplevel(self.ventana)
            ventana_emergente.title("Texto del Enlace")

            # Create a ScrolledText widget with word wrap
            texto_desplazable = scrolledtext.ScrolledText(ventana_emergente, wrap=tk.WORD)
            texto_desplazable.pack(fill=tk.BOTH, expand=True)  # Make the widget expand and fill the window

            texto_enlaces = ""
            for noticia in self.enlaces_encontrados:
                texto_enlaces += f"URL: {noticia['url']}\nTexto: {noticia['texto']}\n\n"

            texto_desplazable.insert(tk.INSERT, texto_enlaces)

        except Exception as e:
            print("Error mostrando texto del enlace", e)

if __name__ == '__main__':
    app = Scrapping()
    app.iniciar()
