import os
import pdfplumber
import docx
import tempfile
import re
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configura tu cliente de Groq
client = Groq(
    api_key="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"
)

# Define los márgenes
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
PAGE_WIDTH, PAGE_HEIGHT = letter
usable_width = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

def clean_text(text):
    # Elimina caracteres no imprimibles
    return re.sub(r'[^\x20-\x7E]+', '', text)

def read_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if file_extension == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += clean_text(page_text) + '\n'  # Limpia el texto al leer
        
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += clean_text(paragraph.text) + '\n'  # Limpia el texto al leer
        
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = clean_text(txt_file.read())  # Limpia el texto al leer
        
        else:
            print("Formato de archivo no soportado.")
            return None

    except Exception as e:
        print(f"Se produjo un error al leer el archivo: {e}")
        return None
    
    return text

def wrap_text(text, max_width, font_size, c):
    """Divide el texto en líneas que se ajusten al ancho máximo."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()  # Usa strip para evitar espacios al principio
        text_width = c.stringWidth(test_line, 'Helvetica', font_size)

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:  # Evita agregar líneas vacías
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)  # Añadir la última línea

    return lines

def generar_resumen(file_path):
    og = read_file(file_path)
    
    if og:
        print("Archivo leído con éxito. Solicitando resumen...")

        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": "Por favor, resume el siguiente texto para estudiantes con TDAH. El resumen debe: \n\n1. Ser más corto y simple, usando un lenguaje claro y directo. \n\n2. Mantener el significado original y los detalles importantes. \n\n3. Conservar el mismo punto de vista y tono que el texto original. \n\n4. Mantener el orden de la información. \n\n No utilices viñetas ni encabezados. \n\n Aquí está el texto:\n\n" + og
                }],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )

            text_content = completion.choices[0].message.content
            if not text_content:
                print("Error: El resumen generado está vacío.")
                return None

            print(f"Resumen generado: \n{text_content}")

            # Crear un archivo temporal para el PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            result_pdf = temp_file.name

            # Crear un PDF y guardar el resumen
            c = canvas.Canvas(result_pdf, pagesize=letter)
            c.setFont("Helvetica", 12)  # Establecer la fuente y tamaño
            y = PAGE_HEIGHT - 50  # Posición inicial en el eje Y

            # Agregar el título al PDF
            c.drawString(MARGIN_LEFT, y, "Resumen del texto:")
            y -= 20  # Espacio después del título

            # Agregar el contenido del resumen al PDF
            lines = wrap_text(text_content, usable_width, 12, c)
            
            # Aumentar el interlineado cambiando el valor de decremento
            interlineado = 20  # Ajusta este valor para aumentar o disminuir el interlineado

            for line in lines:
                c.drawString(MARGIN_LEFT, y, line)
                y -= interlineado  # Espaciado entre líneas
                if y < 50:  # Si llegamos al final de la página, crear una nueva
                    c.showPage()
                    c.setFont("Helvetica", 12)  # Establecer la fuente y tamaño para la nueva página
                    y = PAGE_HEIGHT - 50  # Reiniciar la posición Y para la nueva página
                    c.drawString(MARGIN_LEFT, y, "Resumen del texto:")
                    y -= 20  # Espacio después del título

            c.save()  # Guardar el archivo PDF
            temp_file.close()  # Cerrar el archivo temporal
            print(f"Resumen guardado temporalmente en {result_pdf}")
            
            return result_pdf  # Retornar la ruta del archivo temporal

        except Exception as e:
            print(f"Error durante la generación del resumen: {e}")
            return None

    else:
        print("No se pudo leer el contenido del archivo.")
        return None

