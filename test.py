from flask import Flask, jsonify, request
import os
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from pathlib import Path
import fitz  # PyMuPDF для работы с PDF
from docx import Document
import tiktoken
from openai import OpenAI

app = Flask(__name__)

@app.route('/processUrl')
def greet():
    url = request.args.get('url', 'мир')

    base_url = "https://www.bicotender.ru"
    action = "/login/"
    login_url = requests.compat.urljoin(base_url, action)
    login_data = {
        "login": "client1399145",
        "password": "K1208660325"
    }

    # Создаем сессию
    session = requests.Session()

    # Логинимся
    response = session.post(login_url, data=login_data)
    response.raise_for_status()

    # URL защищенной страницы
    tender_url = url

    # Запрашиваем страницу тендера
    response = session.get(tender_url)
    response.raise_for_status()

    # Парсинг HTML
    soup = BeautifulSoup(response.text, 'html.parser')


    # Текущая рабочая директория
    base_dir = os.getcwd()

    # Каталог для сохранения файлов
    output_dir = os.path.join(base_dir, "temp_files")
    os.makedirs(output_dir, exist_ok=True)

    # Ищем все ссылки на документы
    files_path = []
    for link in soup.find_all('a', href=True):
        if "file_id" in link['href'] and "load" in link['href'] and "/browser/" not in link['href'] and "/all/" not in link['href']:
            doc_url = link['href']
            file_name = link.text.strip()  # Извлекаем текст внутри тега <a>
            
            # Полный путь для сохранения
            file_path = os.path.join(output_dir, file_name)
            
            doc_response = session.get(doc_url)
            if doc_response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(doc_response.content)
                #print(f"Файл сохранён: {file_path}")
                files_path.append(file_path)
            else:
                print(f"Ошибка при скачивании: {doc_response.status_code}")

    # Формируем сложный объект для возврата
    result = {
        "contest_name": "Конкурс №31231",
        "description": ' '.join(files_path)
    }
    
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to Render's port 10000
    app.run(host='0.0.0.0', port=port)