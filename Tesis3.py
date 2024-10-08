from flask import Flask, request, redirect, url_for, render_template, send_file, flash
import os
import tempfile
import fitz  # PyMuPDF
from docx import Document
from pdf2docx import Converter
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from flask_sqlalchemy import SQLAlchemy
from docx2pdf import convert  # Para convertir el archivo .docx a .pdf
import pythoncom
import resumen2


app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), nullable=False) 
    institucion = db.Column(db.String(100), nullable=False)

# Modelo para los Códigos Institucionales Permitidos
class CodigoPermitido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  # códigos únicos permitidos

# Crear la base de datos y las tablas
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        codigo = request.form.get('codigo')
        institucion = request.form.get('institucion')

        # Comprobar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return "Este correo ya está registrado", 400
        
        # Verificar si el código institucional ya está registrado
        codigo_existente = Usuario.query.filter_by(codigo=codigo).first()
        if codigo_existente:
            return "Este código institucional ya está registrado", 400

        # Crear un nuevo usuario
        nuevo_usuario = Usuario(email=email, password=password, codigo=codigo, institucion=institucion)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('login'))  # Redirigir al login tras registrarse

    return render_template('registro.html')


# Ruta para mostrar el formulario de inicio de sesión
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Buscar si el usuario existe en la base de datos
        usuario_existente = Usuario.query.filter_by(email=email).first()

        if not usuario_existente:
            flash('El usuario no existe.', 'error')
        elif usuario_existente.password != password:
            flash('Contraseña incorrecta.', 'error')
        else:
            flash(f'Bienvenido, {email}!', 'success')
            return redirect(url_for('upload'))  # Redirigir a la página de upload o donde desees

    return render_template('login.html')


@app.route('/upload', methods=['GET'])
def upload_file():
    return render_template('upload.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return 'No file part or no selected file'
        
        # Guardar el archivo temporalmente
        nombre_original, extension = os.path.splitext(file.filename)
        ruta_archivo = os.path.join(tempfile.gettempdir(), nombre_original + extension)
        file.save(ruta_archivo)

        dificultad_aprendizaje = request.form.get('dificultad_aprendizaje')
        nombre_fuente = request.form.get('nombre_fuente')
        interlineado = int(request.form.get('interlineado', 14))
        size_fuente = int(request.form.get('size_fuente', 12))
        formato_salida = request.form.get('formato_salida', 'pdf')
        color_fondo = request.form.get('color_fondo')

        if dificultad_aprendizaje == 'TDAH':
            # Llamar a la función de resumen de `resumen2.py`
            resumen_generado = resumen2.generar_resumen(ruta_archivo)
            if resumen_generado:
                return send_file(resumen_generado, as_attachment=True, download_name = f"{nombre_original}_tdah.pdf")
            else:
                return 'Error al generar el resumen.', 500
        elif dificultad_aprendizaje == 'dislexia':
            # Adaptar el archivo para dislexia
            archivo_adaptado = modificar_documento(
                ruta_archivo,
                nombre_fuente=nombre_fuente,
                interlineado=interlineado,
                size_fuente=size_fuente,
                formato_salida=formato_salida,
                color_fondo=color_fondo
            )
            if archivo_adaptado:
                return send_file(archivo_adaptado, as_attachment=True)
            else:
                return 'Error al adaptar el documento.', 500
        elif dificultad_aprendizaje == 'Ambas':
            resumen_generado = resumen2.generar_resumen(ruta_archivo)
            if resumen_generado:
                # Luego aplicar modificaciones para dislexia al resumen
                archivo_adaptado = modificar_documento(
                    resumen_generado,
                    nombre_fuente=nombre_fuente,
                    interlineado=interlineado,
                    size_fuente=size_fuente,
                    formato_salida=formato_salida,
                    color_fondo=color_fondo
                )
                if archivo_adaptado:
                    return send_file(archivo_adaptado, as_attachment=True, download_name=f"{nombre_original}_tdah_dislexia.pdf")
                else:
                    return 'Error al adaptar el resumen para dislexia.', 500
            else:
                return 'Error al generar el resumen.', 500
    return render_template('upload.html')




def convertir_pdf_a_docx(ruta_pdf, ruta_docx):
    cv = Converter(ruta_pdf)
    cv.convert(ruta_docx, start=0, end=None)
    cv.close()


def modificar_pdf(ruta_archivo, nombre_fuente, interlineado, size_fuente, color_fondo):
    doc = fitz.open(ruta_archivo)
    nuevo_doc = fitz.open()

    ancho_a4 = 595
    alto_a4 = 842
    margen_superior = 50

    # Convertir color de fondo hexadecimal a valores RGB
    color_fondo_rgb = tuple(int(color_fondo[i:i+2], 16) / 255 for i in (1, 3, 5))

    for pagina in doc:
        nueva_pagina = nuevo_doc.new_page(width=ancho_a4, height=alto_a4)
        nueva_pagina.draw_rect(fitz.Rect(0, 0, ancho_a4, alto_a4), color=color_fondo_rgb, fill=color_fondo_rgb)

        y_offset = margen_superior
        for bloque in pagina.get_text("dict")["blocks"]:
            if "lines" in bloque:
                for linea in bloque["lines"]:
                    for span in linea["spans"]:
                        texto = span["text"]
                        x, y = span["bbox"][:2]
                        nueva_pagina.insert_text((x, y_offset), texto, fontname=nombre_fuente, fontsize=size_fuente, color=(0, 0, 0))
                    y_offset += size_fuente * 1.8
                y_offset += size_fuente * 0.5

    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_Adaptado.pdf"
    nuevo_doc.save(nombre_archivo_modificado)
    nuevo_doc.close()
    return nombre_archivo_modificado


def modificar_word(ruta_archivo, nombre_fuente, interlineado, size_fuente, color_fondo):
    pythoncom.CoInitialize()  # Inicializa el sistema COM
    try:
        doc = Document(ruta_archivo)
        
        # Aplicar el color de fondo a las páginas de Word
        sectPr = doc.sections[0]._sectPr
        bg = OxmlElement('w:background')
        bg.set(qn('w:color'), color_fondo[1:])  # Eliminamos el símbolo '#' para obtener el color HEX puro
        sectPr.append(bg)

        for parrafo in doc.paragraphs:
            for run in parrafo.runs:
                run.font.name = nombre_fuente
                run.font.size = Pt(size_fuente)

            p = parrafo._element
            pPr = p.get_or_add_pPr()
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:line'), str(int((interlineado + 2) * 1.8 * 20)))
            pPr.append(spacing)

        nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_Adaptado.docx"
        doc.save(nombre_archivo_modificado)
        return nombre_archivo_modificado
    finally:
        pythoncom.CoUninitialize()  # Desinicializa COM


def modificar_documento(ruta_archivo, nombre_fuente, size_fuente, interlineado, formato_salida, color_fondo):
    pythoncom.CoInitialize()  # Inicializa el sistema COM
    try:
        if formato_salida == "pdf":
            # No se añade sufijo extra aquí
            ruta_docx_temp = os.path.splitext(ruta_archivo)[0] + ".docx"
            convertir_pdf_a_docx(ruta_archivo, ruta_docx_temp)
            archivo_docx = modificar_word(ruta_docx_temp, nombre_fuente, interlineado, size_fuente, color_fondo)

            # Convertir el archivo Word a PDF
            archivo_pdf_final = os.path.splitext(ruta_archivo)[0] + "_adaptado.pdf"  # Sufijo solo aquí
            convert(archivo_docx, archivo_pdf_final)

            return archivo_pdf_final

        elif formato_salida == "docx":
            if ruta_archivo.endswith('.pdf'):
                ruta_docx_temp = os.path.splitext(ruta_archivo)[0] + ".docx"
                convertir_pdf_a_docx(ruta_archivo, ruta_docx_temp)
                return modificar_word(ruta_docx_temp, nombre_fuente, interlineado, size_fuente, color_fondo)
            else:
                # Sufijo _adaptado solo aquí
                return modificar_word(ruta_archivo, nombre_fuente, interlineado, size_fuente, color_fondo)
    finally:
        pythoncom.CoUninitialize()  # Desinicializa COM

if __name__ == '__main__':
    app.run(debug=True)
