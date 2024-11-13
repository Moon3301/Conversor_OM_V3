import pdfplumber
import re
from model_train import buscar_examen_similar
import json

#path_PDF = "PDF/Orden_Clinica_Original.pdf"

def extraer_texto_pdf(ruta_pdf):
    texto_completo = ""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    texto_completo += f"--- Página {i + 1} ---\n" + texto + "\n\n"
                else:
                    texto_completo += f"--- Página {i + 1} (sin texto detectado) ---\n\n"
        return texto_completo
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        return None

def extraer_prestaciones(texto, source_clinic):
    # Busca la sección "Prestaciones Solicitadas" después del título correspondiente
    match = re.search(r"Prestaciones Solicitadas\s*Código\s*Descripción\s*(.*?)\s*Av\.", texto, re.DOTALL | re.IGNORECASE)
    print('Match: ',match)
    if match:
        prestaciones_texto = match.group(1)
        print("Texto de prestaciones encontrado:", prestaciones_texto)  # Depuración

        if (source_clinic == 'Clinica_1'):

            examenes = re.findall(r"(\d{6}-\d{2})\s+([^\n]+)", prestaciones_texto)

        if (source_clinic == 'Clinica_2'):

            examenes = re.findall(r"(\d{6})\s+([^\n]+)", prestaciones_texto)
        # Extrae las prestaciones en formato de código y descripción
        # Ajusta para capturar seis dígitos, un guion, y dos dígitos si corresponde
        
        print('Examenes: ',examenes)
        if not examenes:
            print("No se encontraron exámenes en el texto de prestaciones.")

        lista_examenes = [{"codigo": codigo, "examen_original": descripcion.strip()} for codigo, descripcion in examenes]
        return lista_examenes
    else:
        print("No se encontró la sección de 'Prestaciones Solicitadas'")
        return []
    
# Cargar la base de datos de exámenes desde un archivo JSON
def cargar_base_datos_examenes(ruta_json):
    with open(ruta_json, 'r') as f:
        data = json.load(f)
    return data["examenes"]

def conversor_PDF(path_PDF, source_clinic, destination_clinic, ruta_json):
    # Cargar la base de datos de exámenes
    base_datos_examenes = cargar_base_datos_examenes(ruta_json)

    # Extraer texto del PDF
    texto = extraer_texto_pdf(path_PDF)

    if texto:
        print("Texto PDF: ", texto)
        prestaciones = extraer_prestaciones(texto, source_clinic)
        print("Prestaciones: ", prestaciones)
        
        resultados = []
        diccionario = {}
        
        # Recorrer cada examen de la lista de prestaciones
        for examen in prestaciones:
            # Buscar examen similar y similitud
            examen_similar, mejor_similitud = buscar_examen_similar(examen['examen_original'], destination_clinic)
            print(examen_similar, mejor_similitud)

            # Buscar el código del examen similar en la base de datos
            codigo_examen = None
            for item in base_datos_examenes:
                if item["nombre"].lower() == examen_similar.lower():
                    codigo_examen = item["codigo"]
                    break

            # Agregar resultados solo si se encontró un examen similar en la base de datos
            if examen_similar and codigo_examen:
                resultados.append({
                    "codigo": codigo_examen,
                    "examen_modificado": examen_similar,
                    "resultado": mejor_similitud
                })

            # Agregar al diccionario de exámenes encontrados
            diccionario[examen['examen_original']] = examen_similar

        return resultados, diccionario
    else:
        return "No se pudo extraer texto del PDF."