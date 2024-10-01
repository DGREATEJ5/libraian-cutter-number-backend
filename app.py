from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import os
import re
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Health check route
@app.route("/", methods=["GET"])
def health_check():
    logging.debug("Health check route accessed")
    return jsonify({"status": "Model is running"}), 200

def get_last_name(author):
    try:
        patterns = [
            r'^(?P<last>[\w\-\']+),\s*[\w\.\-\']+',  
            r'^(?P<last>[\w\-\']+)$',                
            r'^[\w\.\-\']+\s+(?P<last>[\w\-\']+)$',  
            r'^[\w\.\-\']+\s+(?P<last>[\w\-\']+)\s*$', 
            r'^[\w\.\-\']+\s+(?P<last>[\w\-\']+),',  
            r'^(?P<last>[\w\-\']+\s[\w\-\']+),',     
        ]

        if ',' in author:
            for pattern in patterns:
                match = re.match(pattern, author)
                if match:
                    return match.group('last')
        else:
            name_parts = re.split(r'[,\s]+', author.strip())
            name_parts = [part for part in name_parts if len(part) > 1 or not part.isalpha()]
            titles = ['Dr', 'Mr', 'Mrs', 'Ms', 'Prof']
            name_parts = [part for part in name_parts if part not in titles]
            
            prefixes = ['van', 'de', 'di', 'la', 'da', 'von', 'le', 'del', 'der', 'du', 'van der']
            if len(name_parts) > 1 and name_parts[-2].lower() in prefixes:
                return f"{name_parts[-2]} {name_parts[-1]}"
            
            if len(name_parts) > 1:
                return name_parts[-1]
        
        return author
    except Exception as e:
        logging.error(f"Error in get_last_name: {e}")
        raise

def get_cutter_number(last_name):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        chrome_bin = os.getenv('GOOGLE_CHROME_BIN', '/app/.apt/usr/bin/google-chrome-stable')
        chrome_driver_path = os.getenv('CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver')

        options.binary_location = chrome_bin
        service = ChromeService(executable_path=chrome_driver_path)

        driver = webdriver.Chrome(service=service, options=options)
        driver.get("http://cutternumber.com/")

        try:
            input_field = driver.find_element(By.NAME, "cutText")
            input_field.send_keys(last_name)
            
            submit_button = driver.find_element(By.XPATH, "//button[@onclick='submitCut()']")
            submit_button.click()
            
            cutter_number = driver.find_element(By.ID, "numero_cut").text
        except Exception as e:
            logging.error(f"Error retrieving cutter number: {e}")
            driver.quit()
            return None
        
        driver.quit()
        return cutter_number
    except Exception as e:
        logging.error(f"Error in get_cutter_number: {e}")
        raise

def process_title(title):
    try:
        if title.lower().startswith('the '):
            words = title.split()
            if len(words) > 1:
                return words[1][0].lower()
        return title[0].lower()
    except Exception as e:
        logging.error(f"Error in process_title: {e}")
        raise

@app.route('/get-cutter-number', methods=['POST'])
def cutter_number_endpoint():
    try:
        data = request.json
        author = data.get('author')
        title = data.get('title')
        
        if not author or not title:
            return jsonify({'error': 'Missing author or title'}), 400
        
        last_name = get_last_name(author)
        cutter_number = get_cutter_number(last_name)
        if cutter_number:
            title_letter = process_title(title)
            cutter_number = cutter_number + title_letter
            return jsonify({'cutter_number': cutter_number}), 200
        else:
            return jsonify({'error': 'Failed to retrieve Cutter Number'}), 500
    except Exception as e:
        logging.error(f"Error in cutter_number_endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
