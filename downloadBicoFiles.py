import os
import requests
from bs4 import BeautifulSoup
import zipfile

def extract_zip(file_path, output_dir):
    # Распаковка ZIP-файла
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            # Декодируем имя файла
            decoded_name = file_name.encode('cp437').decode('cp866')

            # Определяем полный путь к файлу
            extracted_path = os.path.join(output_dir, decoded_name)
            # Создаём директорию, если её нет
            if file_name.endswith('/'):  # Если это папка
                os.makedirs(extracted_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                # Извлекаем файл
                with zip_ref.open(file_name) as source, open(extracted_path, 'wb') as target:
                    target.write(source.read())
            #zip_ref.extractall(output_dir)
    os.remove(file_path)

def download_files(bicoUrl, output_dir):
    base_url = "https://www.bicotender.ru"
    action = "/login/"
    login_url = requests.compat.urljoin(base_url, action)
    login_data = {
        "login": "client1399145",
        "password": "K1208660325"
    }

    session = requests.Session()

    # Логинимся
    response = session.post(login_url, data=login_data)
    response.raise_for_status()

    # URL защищенной страницы
    tender_url = bicoUrl

    # Запрашиваем страницу тендера
    response = session.get(tender_url)
    response.raise_for_status()

    # Парсинг HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    os.makedirs(output_dir, exist_ok=True)

    # Ищем все ссылки на документы
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
                _, extension = os.path.splitext(file_path)
                if(extension.lower() == '.zip'):
                    extract_zip(file_path, output_dir)
            else:
                print(f"Ошибка при скачивании: {doc_response.status_code}")

