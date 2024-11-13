import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
import pickle
import os

# Cargar el modelo de embeddings
modelo_embeddings = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Diccionario de ejemplo con exámenes por clínica
examenes_por_clinica = {
    "Clinica_1": 
    [
        "Hemograma Completo",
        "Perfil Lipídico",
        "Prueba de Función Hepática"
    ],
    "Clinica_2": [
        "BIOQUÍMICO GENERAL", "TSH Y T4", "HEMOGRAMA", "PRUEBA RENAL", "PERFIL LIPIDICO", 
        "PERFIL HEPATICO", "PERFIL TIROIDEO", "PERFIL BIOQUIMICO", "PERFIL HORMONAL",
        "PERFIL DE COAGULACION", "PERFIL DE ORINA COMPLETO", "PERFIL DE ORINA SIMPLE",
        "EXAMEN DE GLUCOSA", "EXAMEN DE COLESTEROL", "EXAMEN DE TRIGLICERIDOS",
        "EXAMEN VITAMINA B12", "EXAMEN DE ACIDO FOLICO", "EXAMEN DE TSH",
        "TIROXINA LIBRE", "PERFIL DE INSULINA", "TESTOSTERONA EN SANGRE", "TESTOSTERONA LIBRE",
        "VITAMINA D:25", "SANGRE VENOSA"
    ]
}

# Función para generar y guardar embeddings para una clínica específica
def generar_y_guardar_embeddings(clinica, examenes, filename):
    diccionario_embeddings = {examen: modelo_embeddings.encode(examen) for examen in examenes}
    with open(filename, 'wb') as file:
        pickle.dump(diccionario_embeddings, file)
    print(f"Embeddings generados y guardados para {clinica} en {filename}")

# Función para cargar embeddings de una clínica específica
def cargar_embeddings(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)

# Función principal para cargar o generar embeddings según la clínica
def obtener_embeddings_clinica(clinica):
    # Define el nombre del archivo para la clínica específica
    filename = f'embeddings_{clinica}.pkl'
    
    # Verifica si los embeddings de la clínica ya existen
    if os.path.exists(filename):
        print(f"Embeddings cargados desde {filename} para {clinica}")
        return cargar_embeddings(filename)
    else:
        # Generar embeddings si el archivo no existe
        print(f"No se encontró el archivo para {clinica}. Generando embeddings...")
        examenes = examenes_por_clinica.get(clinica, [])
        if not examenes:
            print(f"No se encontraron exámenes para la clínica {clinica}.")
            return None
        generar_y_guardar_embeddings(clinica, examenes, filename)
        return cargar_embeddings(filename)

# Función para buscar el examen más similar en una clínica específica
def buscar_examen_similar(nombre_examen, clinica):
    # Obtener los embeddings de la clínica
    diccionario_embeddings = obtener_embeddings_clinica(clinica)
    if diccionario_embeddings is None:
        print(f"No se encontraron exámenes para la clínica {clinica}.")
        return
    
    # Preparar los datos de embeddings y nombres
    examenes_nombres = list(diccionario_embeddings.keys())
    examenes_embeddings_tensor = torch.tensor(np.array(list(diccionario_embeddings.values())))

    # Generar embedding del examen ingresado
    embedding_input = modelo_embeddings.encode(nombre_examen, convert_to_tensor=True)

    # Calcular la similitud
    similitudes = util.pytorch_cos_sim(embedding_input, examenes_embeddings_tensor)
    mejor_similitud, indice_mejor = torch.max(similitudes, 1)
    mejor_similitud = mejor_similitud.item()

    # Validar si la similitud es suficiente
    umbral_similitud = 0.5
    if mejor_similitud >= umbral_similitud:
        examen_similar = examenes_nombres[indice_mejor]
        print(f"Examen ingresado: {nombre_examen} | Examen similar en {clinica}: {examen_similar} | Similitud: {mejor_similitud:.2f}")
        return examen_similar, mejor_similitud
        
    else:
        print(f"No se encontró un examen similar para '{nombre_examen}' en {clinica} con suficiente precisión (similitud: {mejor_similitud:.2f}).")