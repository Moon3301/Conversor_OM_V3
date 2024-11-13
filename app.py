from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for
from generar_pdf import insertar_examenes_en_pdf_con_rectangulos
from lector_pdf import conversor_PDF  # Importar función para procesamiento del PDF
import os
import tempfile

app = Flask(__name__)

PDF_DIRECTORY = "public/pdfs"
os.makedirs(PDF_DIRECTORY, exist_ok=True)

@app.route('/')
def index():
    # Renderiza el HTML en blanco (index.html) para cargar luego la información
    return render_template('index.html')

@app.route('/public/pdfs/<path:filename>')
def serve_pdf(filename):
    # Sirve el archivo PDF desde el directorio pdfs
    return send_from_directory(PDF_DIRECTORY, filename)

@app.route('/procesar_pdf', methods=['POST'])
def procesar_pdf():
    # Llama a la función que procesa el PDF

    path_PDF = request.files.get('path_PDF')
    source_clinic = request.form.get('source_clinic')
    destination_clinic = request.form.get('destination_clinic')

    if path_PDF:

        print(f"Procesando PDF: {path_PDF} | Clínica de origen: {source_clinic}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf_path = temp_pdf.name
            path_PDF.save(temp_pdf_path)

        resultados, diccionario = conversor_PDF(path_PDF, source_clinic, destination_clinic, f"database/data_{destination_clinic}.json")
        
        try:

            pdf_modificado_path = insertar_examenes_en_pdf_con_rectangulos(destination_clinic, resultados, PDF_DIRECTORY)
            # Renderiza la página con los resultados o redirige
            print('Resultados: ',resultados)
            print('pdf_modificado_path:', pdf_modificado_path)
            
            return jsonify(resultados=resultados, pdf_modificado_path = f"/public/pdfs/{os.path.basename(pdf_modificado_path)}")
        
        finally:
            os.remove(temp_pdf_path)
    else:
        print("No se ha recibido ningún archivo PDF.")
        return jsonify(error="No se ha recibido ningún archivo PDF."), 400

if __name__ == '__main__':
    app.run(debug=True)