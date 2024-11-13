import fitz
from fitz import get_text_length
import re
import os
import datetime

TEMPLATES_DIRECTORY = "public/plantillas"

def insertar_examenes_en_pdf_con_rectangulos(clinica, examenes_a_insertar, output_directory):
    """
    Modifica un PDF de plantilla basado en la clínica especificada y agrega exámenes sin fondo opaco.

    Args:
        clinica (str): Nombre de la clínica para seleccionar la plantilla correspondiente.
        examenes_a_insertar (list): Lista de diccionarios o strings con los exámenes a agregar.
        output_directory (str): Directorio donde se guardará el PDF modificado.

    Returns:
        str: Ruta del PDF modificado.
    """
    # Seleccionar el PDF de plantilla basado en la clínica
    plantilla_pdf_path = os.path.join(f"{TEMPLATES_DIRECTORY}/{clinica}", f"orden_medica_vacia_{clinica}.pdf")
    if not os.path.exists(plantilla_pdf_path):
        raise FileNotFoundError(f"No se encontró la plantilla para la clínica '{clinica}'")

    # Abrir la plantilla de PDF
    pdf_documento = fitz.open(plantilla_pdf_path)
    
    # Iterar sobre cada página del documento para buscar la sección "Prestaciones Solicitadas"
    for page_num in range(pdf_documento.page_count):
        pagina = pdf_documento[page_num]
        
        # Buscar el texto "Prestaciones Solicitadas" para determinar el punto de inserción
        texto_pagina = pagina.get_text("text")
        match = re.search(r"Prestaciones Solicitadas", texto_pagina, re.IGNORECASE)
        
        if match:
            # Encontrar las posiciones de "Código" y "Descripción"
            codigo_rect = pagina.search_for("Código")[0]
            descripcion_rect = pagina.search_for("Descripción")[0]
            
            # Definir el punto inicial para la inserción de los exámenes
            pos_y = codigo_rect.y1 + 20  # Ajustar la posición de inserción justo debajo de "Código"
            
            # Ajustar el espacio entre líneas y tamaño de fuente
            espacio_entre_lineas = 15
            font_size = 10
            
            # Insertar cada examen en el PDF
            for examen in examenes_a_insertar:
                # Manejar tanto diccionarios como strings
                if isinstance(examen, dict):
                    codigo = examen.get('codigo', '')
                    descripcion = examen.get('examen_modificado', '')
                else:
                    # Si es un string, asumimos que es la descripción y dejamos el código vacío
                    codigo = ''
                    descripcion = str(examen)

                # Posición para el código
                pos_x_codigo = codigo_rect.x0
                
                # Posición para la descripción
                pos_x_descripcion = descripcion_rect.x0
                
                # Calcular el ancho del texto
                codigo_width = fitz.get_text_length(codigo, fontname="helv", fontsize=font_size)
                descripcion_width = fitz.get_text_length(descripcion, fontname="helv", fontsize=font_size)

                # Ajustar el rectángulo para que se alinee con el texto
                rect_height = font_size + 6
                rect_prestacion = fitz.Rect(
                    pos_x_codigo, 
                    pos_y, 
                    max(pos_x_descripcion + descripcion_width + 8, descripcion_rect.x1), 
                    pos_y + rect_height
                )
                pagina.draw_rect(rect_prestacion, color=(0, 0, 0), width=0.5)

                # Insertar el código del examen
                text_y = pos_y + (rect_height - font_size) / 2
                pagina.insert_text((pos_x_codigo + 4, text_y), codigo, fontsize=font_size, fontname="helv", color=(0, 0, 0))
                
                # Insertar la descripción del examen
                pagina.insert_text((pos_x_descripcion + 4, text_y), descripcion, fontsize=font_size, fontname="helv", color=(0, 0, 0))
                
                # Ajustar el espacio entre líneas
                espacio_entre_lineas = rect_height + 2
                pos_y += espacio_entre_lineas  # Mover hacia abajo para el siguiente examen

            break  # Asumimos que las prestaciones solo se insertan en la primera página que contiene la sección

    # Guardar el PDF modificado en el directorio designado
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_modificado_path = os.path.join(output_directory, f"PDF_modificado_{date_time}.pdf")
    pdf_documento.save(pdf_modificado_path)
    pdf_documento.close()
    
    return pdf_modificado_path
