# Web Scraping en Marca.com

Este proyecto consiste en un programa para realizar web scraping en el sitio web Marca.com, específicamente en las 5 secciones para obtener información relevante de las noticias.

## Instalación

### Requisitos
- Python 3.x instalado

### Pasos de instalación
1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias necesarias ejecutando `pip install -r requirements.txt`.
3. Asegúrate de tener los paquetes requeridos, como `requests`, `beautifulsoup4`, `spacy`, entre otros.

## Uso

### Ejecución
1. Para ejecutar la aplicación, abre una terminal en la carpeta donde se encuentran los archivos del proyecto.
2. Ejecuta el archivo correspondiente a la versión que deseas utilizar, por ejemplo, `python v1_scraper.py`.

### Interacción
- En cada versión del programa se presenta una interfaz diferente para interactuar con el scraping de la web de Marca.com.
- En las primeras versiones, se proporcionan resultados en la consola, mientras que en versiones posteriores se incluyen gráficos y funcionalidades de interfaz gráfica.

## Cambios en las Versiones

### v1:
- Realiza scraping de enlaces de noticias y muestra los párrafos de cada noticia en la consola.

### v2:
- Mejora la extracción de datos al acceder a subpáginas de noticias directamente desde la página principal.
- Muestra el texto completo de las subpáginas en la consola.

### v3:
- Agrega análisis de frecuencia de palabras utilizando `spaCy` y `matplotlib`.
- Presenta un gráfico de pastel y una tabla con las palabras más frecuentes y enlaces asociados.

### v4:
- Incluye una interfaz gráfica utilizando `tkinter`.
- Permite buscar palabras clave relacionadas con deportes específicos.
- Muestra las palabras más comunes en gráficos y proporciona la funcionalidad para ver el texto de los enlaces encontrados.

---
Autor:
[HectorCRZBQ](https://github.com/HectorCRZBQ)
