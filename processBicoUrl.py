from datetime import datetime
import shutil
import time
import os
from docx import Document
from flask import Flask, request
import requests
from downloadBicoFiles import download_files
from TalkWithOpenAI import ask_questions

def get_tener_no(url):
    # Разбить строку по символу "/"
    parts = url.strip('/').split('/')
    return parts[-1]

app = Flask(__name__)
@app.route('/processUrl')
def main():
    time1 = datetime.now()
    url = request.args.get('url', 'https://www.bicotender.ru/tc/tender/show/tender_id/282439881/')
    #url = 'https://www.bicotender.ru/tc/tender/show/tender_id/282439881/'

    # Текущая рабочая директория
    base_dir = os.getcwd()

    # Каталог для сохранения файлов
    output_dir = os.path.join(base_dir, "temp_files")
    # Проверяем, существует ли каталог
    if os.path.exists(output_dir):
        # Удаляем каталог и все его содержимое
        shutil.rmtree(output_dir)

    download_files(url, output_dir)

    # Считываем promt из файла
    response = requests.get('https://onedrive.live.com/download?cid=7A4DFCE935F80DB4&resid=7A4DFCE935F80DB4!34343&authkey=!AIAERGoRU5EhwdA', stream=True)

    # Проверяем, успешно ли выполнен запрос
    if response.status_code == 200:
        file_path = os.path.join(output_dir, 'promt.docx')
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f'Ошибка при скачивании файла: {response.status_code}')

    doc = Document(file_path)
    questions = [p.text for p in doc.paragraphs if p.text != ""]
    os.remove(file_path)
    res = ask_questions(output_dir, questions)
   
    #file_path = os.path.join(output_dir, 'res.html')
    #with open(file_path, 'w') as file:
    #    file.write(res)

    time2 = datetime.now()
    time_difference = time2 - time1
    minutes, seconds = divmod(time_difference.seconds, 60)

    print(f"Прошло времени: {minutes}:{seconds}")
    tender_no = get_tener_no(url)

    # Формируем сложный объект для возврата
    result = {
        "contest_name": tender_no,
        "description": res
    }
    return result
    #return res

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to Render's port 10000
    app.run(host='0.0.0.0', port=port)

#main()