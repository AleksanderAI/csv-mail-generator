from flask import Flask, render_template, request, jsonify
import csv
import io
import os
import codecs
import re

app = Flask(__name__)

# Szablony tekstów w różnych językach
TEMPLATES = {
    'pl': {
        'header': "Dzień dobry,\n\nprzesyłam nasze nowe zamówienie:\n",
        'footer': "\n\nDostawa na adres:\n\nCalvado\nGraniczna 4\n00-130 Warszawa",
        'errors': {
            'no_file': 'Nie wybrano pliku',
            'not_csv': 'Wybrany plik nie jest plikiem CSV',
            'decode_error': 'Nie udało się odczytać pliku. Sprawdź czy plik jest w prawidłowym formacie.'
        }
    },
    'en': {
        'header': "Hello,\n\nI am sending our new order:\n",
        'footer': "\n\nDelivery address:\n\nCalvado\nGraniczna 4\n00-130 Warsaw\nPoland",
        'errors': {
            'no_file': 'No file selected',
            'not_csv': 'Selected file is not a CSV file',
            'decode_error': 'Could not read the file. Please check if the file is in the correct format.'
        }
    }
}

def try_decode_content(file_content, encodings=['utf-8', 'windows-1250', 'iso-8859-2', 'cp1250']):
    for encoding in encodings:
        try:
            return encoding, file_content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None, None

def process_csv_content(file, language='pl'):
    try:
        # Read raw bytes from file
        file_content = file.read()
        
        # Try different encodings
        encoding, content = try_decode_content(file_content)
        
        if not content:
            return {
                'success': False,
                'error': TEMPLATES[language]['errors']['decode_error']
            }
            
        csv_file = io.StringIO(content)
        reader = csv.reader(csv_file)
        
        # Skip the first row
        next(reader, None)
        
        # Process each line according to the rules
        processed_lines = []
        for row in reader:
            if len(row) >= 3:  # Upewnij się, że mamy wszystkie potrzebne kolumny
                # Wyciągnij wartości z kolumn, usuwając cudzysłowy i spacje
                col1 = row[1].strip().strip('"')  # Numer (747211)
                col2 = row[2].strip().strip('"').split(',')[0].strip()  # Liczba przed przecinkiem (1)
                
                # Połącz w format "747211 - 1"
                line = f"{col1} - {col2}"
                
                if line:  # Only add non-empty lines
                    processed_lines.append(line)
        
        # Użyj szablonów w wybranym języku
        template = TEMPLATES[language]
        final_content = template['header'] + '\n'.join(processed_lines) + template['footer']
        
        return {
            'success': True,
            'content': final_content
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    # Get selected language, default to Polish
    language = request.form.get('language', 'pl')
    if language not in TEMPLATES:
        language = 'pl'
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['no_file']})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['no_file']})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['not_csv']})
    
    result = process_csv_content(file, language)
    return jsonify(result)

if __name__ == '__main__':
    # Używamy portu z zmiennej środowiskowej (wymagane przez Render) lub domyślnego 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
