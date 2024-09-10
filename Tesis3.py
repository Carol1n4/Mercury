'''
from flask import Flask, request, jsonify, render_template, send_file
import os
import fitz  # PyMuPDF
from docx import Document
from pdf2docx import Converter
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement 

app = Flask(__name__)

# Ruta para el formulario de carga
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Ruta para manejar la carga y adaptación del archivo
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        ruta_archivo = os.path.join('static', file.filename)
        file.save(ruta_archivo)  # Guarda el archivo en el servidor

        # Llamar a la función de adaptación de contenido
        nombre_archivo_modificado = modificar_documento(ruta_archivo, nombre_fuente="Arial", interlineado=14, contraste=1.2, formato_salida="pdf", color_fondo="#FFFFDD")


        # Devuelve el archivo modificado al usuario
        return send_file(nombre_archivo_modificado, as_attachment=True)



def convertir_pdf_a_docx(ruta_pdf, ruta_docx):
    cv = Converter(ruta_pdf)
    cv.convert(ruta_docx, start=0, end=None)
    cv.close()

def modificar_pdf(ruta_archivo, nombre_fuente, interlineado, contraste, color_fondo):
    doc = fitz.open(ruta_archivo)
    nuevo_doc = fitz.open()  # Crear un nuevo documento PDF

    ancho_a4 = 595
    alto_a4 = 842
    margen_superior = 50
    margen_inferior = 50
    margen_izquierdo = 50
    margen_derecho = 50

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
                        fuente = "helv"
                        tamano = interlineado + 2
                        x, y = span["bbox"][:2]
                        if x < margen_izquierdo:
                            x = margen_izquierdo
                        if x + fitz.get_text_length(texto, fontname=fuente, fontsize=tamano) > ancho_a4 - margen_derecho:
                            x = ancho_a4 - margen_derecho - fitz.get_text_length(texto, fontname=fuente, fontsize=tamano)
                        if y_offset + tamano < alto_a4 - margen_inferior:
                            nueva_pagina.insert_text((x, y_offset), texto, fontname=fuente, fontsize=tamano, color=(0, 0, 0))
                    y_offset += tamano * 1.8
                y_offset += tamano * 0.5

    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.pdf"
    nuevo_doc.save(nombre_archivo_modificado)
    nuevo_doc.close()

def modificar_word(ruta_archivo, nombre_fuente, interlineado, contraste):
    doc = Document(ruta_archivo)
    for parrafo in doc.paragraphs:
        for run in parrafo.runs:
            run.font.name = nombre_fuente
            run.font.size = Pt(interlineado + 2)
        p = parrafo._element
        pPr = p.get_or_add_pPr()
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:line'), str(int((interlineado + 2) * 1.8 * 20)))
        pPr.append(spacing)
    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.docx"
    doc.save(nombre_archivo_modificado)

def modificar_documento(ruta_archivo, nombre_fuente="Arial", interlineado=14, contraste=1.2, formato_salida="pdf", color_fondo="#FFFFDD"):
    if formato_salida == "pdf":
        modificar_pdf(ruta_archivo, nombre_fuente, interlineado, contraste, color_fondo)
    elif formato_salida == "docx":
        if ruta_archivo.endswith('.pdf'):
            ruta_docx_temp = os.path.splitext(ruta_archivo)[0] + "_temp.docx"
            convertir_pdf_a_docx(ruta_archivo, ruta_docx_temp)
            modificar_word(ruta_docx_temp, nombre_fuente, interlineado, contraste)
            os.remove(ruta_docx_temp)
        else:
            modificar_word(ruta_archivo, nombre_fuente, interlineado, contraste)
    else:
        raise ValueError("Formato de salida no soportado")


if __name__ == '__main__':
    app.run(debug=True)
'''
'''
from flask import Flask, request, jsonify, render_template, send_file
import os
import fitz  # PyMuPDF
from docx import Document
from pdf2docx import Converter
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

app = Flask(__name__)

# Ruta para el formulario de carga
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Ruta para manejar la carga y adaptación del archivo
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        ruta_archivo = os.path.join('static', file.filename)
        file.save(ruta_archivo)  # Guarda el archivo en el servidor

        # Llamar a la función de adaptación de contenido
        nombre_archivo_modificado = modificar_documento(ruta_archivo, nombre_fuente="Arial", interlineado=14, contraste=1.2, formato_salida="pdf", color_fondo="#FFFFDD")

        # Verificar si el archivo modificado existe antes de devolverlo
        if os.path.exists(nombre_archivo_modificado):
            return send_file(nombre_archivo_modificado, as_attachment=True)
        else:
            return 'El archivo adaptado no se encontró', 404

def convertir_pdf_a_docx(ruta_pdf, ruta_docx):
    cv = Converter(ruta_pdf)
    cv.convert(ruta_docx, start=0, end=None)
    cv.close()

def modificar_pdf(ruta_archivo, nombre_fuente, interlineado, contraste, color_fondo):
    doc = fitz.open(ruta_archivo)
    nuevo_doc = fitz.open()  # Crear un nuevo documento PDF

    ancho_a4 = 595
    alto_a4 = 842
    margen_superior = 50
    margen_inferior = 50
    margen_izquierdo = 50
    margen_derecho = 50

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
                        fuente = "helv"
                        tamano = interlineado + 2
                        x, y = span["bbox"][:2]
                        if x < margen_izquierdo:
                            x = margen_izquierdo
                        if x + fitz.get_text_length(texto, fontname=fuente, fontsize=tamano) > ancho_a4 - margen_derecho:
                            x = ancho_a4 - margen_derecho - fitz.get_text_length(texto, fontname=fuente, fontsize=tamano)
                        if y_offset + tamano < alto_a4 - margen_inferior:
                            nueva_pagina.insert_text((x, y_offset), texto, fontname=fuente, fontsize=tamano, color=(0, 0, 0))
                    y_offset += tamano * 1.8
                y_offset += tamano * 0.5

    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.pdf"
    nuevo_doc.save(nombre_archivo_modificado)
    nuevo_doc.close()
    return nombre_archivo_modificado

def modificar_word(ruta_archivo, nombre_fuente, interlineado, contraste):
    doc = Document(ruta_archivo)
    for parrafo in doc.paragraphs:
        for run in parrafo.runs:
            run.font.name = nombre_fuente
            run.font.size = Pt(interlineado + 2)
        p = parrafo._element
        pPr = p.get_or_add_pPr()
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:line'), str(int((interlineado + 2) * 1.8 * 20)))
        pPr.append(spacing)
    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.docx"
    doc.save(nombre_archivo_modificado)
    return nombre_archivo_modificado

def modificar_documento(ruta_archivo, nombre_fuente="Arial", interlineado=14, contraste=1.2, formato_salida="pdf", color_fondo="#FFFFDD"):
    if formato_salida == "pdf":
        return modificar_pdf(ruta_archivo, nombre_fuente, interlineado, contraste, color_fondo)
    elif formato_salida == "docx":
        if ruta_archivo.endswith('.pdf'):
            ruta_docx_temp = os.path.splitext(ruta_archivo)[0] + "_temp.docx"
            convertir_pdf_a_docx(ruta_archivo, ruta_docx_temp)
            return modificar_word(ruta_docx_temp, nombre_fuente, interlineado, contraste)
        else:
            return modificar_word(ruta_archivo, nombre_fuente, interlineado, contraste)
    else:
        raise ValueError("Formato de salida no soportado")


if __name__ == '__main__':
    app.run(debug=True)

'''
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

# Ruta para el formulario de carga
@app.route('/upload', methods=['GET'])
def upload_file():
    return render_template('upload.html')

# Ruta para manejar la carga y adaptación del archivo
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Usar un directorio temporal para guardar el archivo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            ruta_archivo = temp_file.name
            file.save(ruta_archivo)  # Guarda el archivo en el directorio temporal

        # Obtener parámetros adicionales del formulario
        nombre_fuente = request.form.get('nombre_fuente')
        interlineado = int(request.form.get('interlineado', 14))
        size_fuente = int(request.form.get('size_fuente', 12))
        formato_salida = request.form.get('formato_salida', 'pdf')
        color_fondo = request.form.get('color_fondo')

        # Llamar a la función de adaptación de contenido
        nombre_archivo_modificado = modificar_documento(
            ruta_archivo, 
            nombre_fuente=nombre_fuente, 
            interlineado=interlineado, 
            size_fuente=size_fuente,
            formato_salida=formato_salida, 
            color_fondo=color_fondo
        )

        # Verificar si el archivo modificado existe antes de devolverlo
        if os.path.exists(nombre_archivo_modificado):
            return send_file(nombre_archivo_modificado, as_attachment=True)
        else:
            return 'El archivo adaptado no se encontró', 404

def convertir_pdf_a_docx(ruta_pdf, ruta_docx):
    cv = Converter(ruta_pdf)
    cv.convert(ruta_docx, start=0, end=None)
    cv.close()

def modificar_pdf(ruta_archivo, nombre_fuente, interlineado, size_fuente, color_fondo):
    
    doc = fitz.open(ruta_archivo)
    nuevo_doc = fitz.open()  # Crear un nuevo documento PDF

    ancho_a4 = 595
    alto_a4 = 842
    margen_superior = 50
    margen_inferior = 50
    margen_izquierdo = 50
    margen_derecho = 50

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
                        if x < margen_izquierdo:
                            x = margen_izquierdo
                        if x + fitz.get_text_length(texto, fontname= nombre_fuente, fontsize=size_fuente) > ancho_a4 - margen_derecho:
                            x = ancho_a4 - margen_derecho - fitz.get_text_length(texto, fontname=nombre_fuente, fontsize= size_fuente)
                        if x + fitz.get_text_length(texto, fontname=nombre_fuente, fontsize=size_fuente) > ancho_a4 - margen_izquierdo:
                            x = ancho_a4 - margen_izquierdo - fitz.get_text_length(texto, fontname=nombre_fuente, fontsize=size_fuente)
                        if y_offset + size_fuente < alto_a4 - margen_inferior:
                            nueva_pagina.insert_text((x, y_offset), texto, fontname=nombre_fuente, fontsize=size_fuente, color=(0, 0, 0))
                    y_offset += size_fuente * 1.8
                y_offset += size_fuente * 0.5

    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.pdf"
    nuevo_doc.save(nombre_archivo_modificado)
    nuevo_doc.close()
    return nombre_archivo_modificado


def modificar_word(ruta_archivo, nombre_fuente, interlineado, color_fondo, size_fuente):
    doc = Document(ruta_archivo)
    color_fondo = request.form.get('color_fondo')
    for parrafo in doc.paragraphs:
        for run in parrafo.runs:
            run.font.name = nombre_fuente
            run.font.size = size_fuente
            #cambia el color de la pagina
            run.page_color = color_fondo
        p = parrafo._element
        pPr = p.get_or_add_pPr()
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:line'), str(int((interlineado + 2) * 1.8 * 20)))
        pPr.append(spacing)
    nombre_archivo_modificado = os.path.splitext(ruta_archivo)[0] + "_adaptado.docx"
    doc.save(nombre_archivo_modificado)
    return nombre_archivo_modificado

def modificar_documento(ruta_archivo, nombre_fuente, size_fuente, interlineado, formato_salida, color_fondo):
    if formato_salida == "pdf":
        return modificar_pdf(ruta_archivo, nombre_fuente, interlineado, size_fuente, color_fondo)
    elif formato_salida == "docx":
        if ruta_archivo.endswith('.pdf'):
            ruta_docx_temp = os.path.splitext(ruta_archivo)[0] + "_temp.docx"
            convertir_pdf_a_docx(ruta_archivo, ruta_docx_temp)
            return modificar_word(ruta_docx_temp, nombre_fuente, interlineado, size_fuente)
        else:
            return modificar_word(ruta_archivo, nombre_fuente, interlineado, size_fuente)
    else:
        raise ValueError("Formato de salida no soportado")

if __name__ == '__main__':
    app.run(debug=True)

