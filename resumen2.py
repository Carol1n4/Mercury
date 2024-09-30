import os
import datetime
import pdfplumber
import docx
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configura tu cliente de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

file_path = 'textos.pdf'

def read_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if file_extension == '.pdf':
            # Leer archivo PDF
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
        
        elif file_extension == '.docx':
            # Leer archivo Word
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
        
        elif file_extension == '.txt':
            # Leer archivo TXT
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
        
        else:
            print("Formato de archivo no soportado.")
            return None

    except Exception as e:
        print(f"Se produjo un error al leer el archivo: {e}")
        return None
    
    return text

# Leer el archivo y almacenar el contenido en 'og'
og = read_file(file_path)

if og:  # Asegúrate de que 'og' no sea None
    # Crear el prompt para la API de Groq
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": "Por favor, resume el siguiente texto para estudiantes con TDAH. El resumen debe: \n\n1. Ser más corto y simple, usando un lenguaje claro y directo. \n\n2. Mantener el significado original y los detalles importantes. \n\n3. Conservar el mismo punto de vista y tono que el texto original. \n\n4. Mantener el orden de la información. \n\n No utilices viñetas ni encabezados. \n\n Aquí está el texto:\n\n" + og
            },
            {
                "role": "assistant",
                "content": "Déjame ayudarte con eso.\n\nPara resumir un texto para estudiantes con TDAH, lo desglosaré en partes más pequeñas y utilizaré un lenguaje simple para que sea fácil de seguir. Por favor, proporciona el texto que deseas resumir.\n\n"
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # Generar un nombre de archivo basado en la fecha y hora actuales
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    result_pdf = f"summary_{timestamp}.pdf"

    # Crear un PDF y guardar el resumen
    c = canvas.Canvas(result_pdf, pagesize=letter)
    c.drawString(72, 720, "Resumen del texto:")  # Título en el PDF

    # Agregar el contenido del resumen al PDF
    text_content = completion.choices[0].message.content
    lines = text_content.split('\n')
    
    y = 680  # Posición inicial en el eje Y
    for line in lines:
        c.drawString(72, y, line)
        y -= 15  # Espaciado entre líneas
        if y < 72:  # Si llegamos al final de la página, crear una nueva
            c.showPage()
            y = 720  # Reiniciar la posición Y

    c.save()  # Guardar el archivo PDF
else:
    print("No se pudo leer el contenido del archivo.")
