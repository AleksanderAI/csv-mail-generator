from flask import Flask, render_template, request, jsonify
import csv
import io
import os
import codecs
import re
import logging

app = Flask(__name__)

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Szablony tekstów w różnych językach
TEMPLATES = {
    'pl': {
        'header': "Dzień dobry,\n\nprzesyłam nasze nowe zamówienie:\n",
        'footer': "\n\nDostawa na adres:\n\nCalvado\nGraniczna 4\n00-130 Warszawa",
        'errors': {
            'no_file': 'Nie wybrano pliku',
            'not_csv': 'Wybrany plik nie jest plikiem CSV',
            'decode_error': 'Nie udało się odczytać pliku. Sprawdź czy plik jest w prawidłowym formacie.',
            'empty_file': 'Plik jest pusty',
            'invalid_format': 'Nieprawidłowy format pliku CSV. Upewnij się, że plik ma odpowiednią strukturę.'
        }
    },
    'en': {
        'header': "Hello,\n\nI am sending our new order:\n",
        'footer': "\n\nDelivery address:\n\nCalvado\nGraniczna 4\n00-130 Warsaw\nPoland",
        'errors': {
            'no_file': 'No file selected',
            'not_csv': 'Selected file is not a CSV file',
            'decode_error': 'Could not read the file. Please check if the file is in the correct format.',
            'empty_file': 'File is empty',
            'invalid_format': 'Invalid CSV format. Please make sure the file has the correct structure.'
        }
    }
}

def try_decode_content(file_content, encodings=['utf-8', 'windows-1250', 'iso-8859-2', 'cp1250', 'latin1']):
    for encoding in encodings:
        try:
            decoded_content = file_content.decode(encoding)
            logger.info(f"Successfully decoded file using {encoding} encoding")
            return encoding, decoded_content
        except UnicodeDecodeError:
            logger.debug(f"Failed to decode with {encoding}")
            continue
    return None, None

def process_csv_content(file, language='pl'):
    try:
        # Read raw bytes from file
        file_content = file.read()
        logger.info(f"Read file: {file.filename}, size: {len(file_content)} bytes")
        
        if len(file_content) == 0:
            logger.error("Empty file uploaded")
            return {
                'success': False,
                'error': TEMPLATES[language]['errors']['empty_file']
            }
        
        # Try different encodings
        encoding, content = try_decode_content(file_content)
        
        if not content:
            logger.error("Could not decode file content with any encoding")
            return {
                'success': False,
                'error': TEMPLATES[language]['errors']['decode_error']
            }
            
        csv_file = io.StringIO(content)
        reader = csv.reader(csv_file)
        
        # Get all rows
        rows = list(reader)
        
        if len(rows) < 2:  # Check if file has header and at least one row
            logger.error("File has insufficient rows")
            return {
                'success': False,
                'error': TEMPLATES[language]['errors']['invalid_format']
            }
        
        # Skip the header row
        rows = rows[1:]
        logger.info(f"Processing {len(rows)} rows")
        
        # Process each line according to the rules
        processed_lines = []
        for row_num, row in enumerate(rows, start=2):
            try:
                if len(row) >= 3:
                    # Wyciągnij wartości z kolumn, usuwając cudzysłowy i spacje
                    col1 = row[1].strip().strip('"')  # Numer (747211)
                    col2 = row[2].strip().strip('"').split(',')[0].strip()  # Liczba przed przecinkiem (1)
                    
                    # Połącz w format "747211 - 1"
                    line = f"{col1} - {col2}"
                    
                    if line and not line.isspace():  # Only add non-empty lines
                        processed_lines.append(line)
                        logger.debug(f"Processed row {row_num}: {line}")
            except Exception as e:
                logger.warning(f"Error processing row {row_num}: {str(e)}")
                continue
        
        if not processed_lines:
            logger.error("No valid lines found in the file")
            return {
                'success': False,
                'error': TEMPLATES[language]['errors']['invalid_format']
            }
        
        # Użyj szablonów w wybranym języku
        template = TEMPLATES[language]
        final_content = template['header'] + '\n'.join(processed_lines) + template['footer']
        
        logger.info("Successfully processed file")
        return {
            'success': True,
            'content': final_content
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    try:
        # Get selected language, default to Polish
        language = request.form.get('language', 'pl')
        if language not in TEMPLATES:
            language = 'pl'
        
        logger.info(f"Processing request with language: {language}")
        
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['no_file']})
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['no_file']})
        
        if not file.filename.endswith('.csv'):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'success': False, 'error': TEMPLATES[language]['errors']['not_csv']})
        
        result = process_csv_content(file, language)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Używamy portu z zmiennej środowiskowej (wymagane przez Render) lub domyślnego 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
