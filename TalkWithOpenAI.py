import os
from pathlib import Path
from docx import Document
import fitz
from openai import OpenAI
import tiktoken
#import win32com.client

def clean_file(file_path, output_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()

    # Удаляем некорректные байты
    cleaned_data = raw_data.decode('utf-8', errors='ignore').encode('utf-8')

    with open(output_path, 'wb') as file:
        file.write(cleaned_data)

def extract_text_from_txt(file_path):
    clean_file(file_path, file_path)
    with open(file_path, "r", encoding='utf-8') as f:
        return f.read()

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# Функция для извлечения текста из DOCX
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

# Функция для извлечения текста из DOCX
# def extract_text_from_doc(file_path):
#     # Создаем объект COM для Microsoft Word
#     word = win32com.client.Dispatch("Word.Application")

#     # Открываем DOC-файл
#     doc = word.Documents.Open(file_path)

#     # Извлекаем текст из документа
#     text = doc.Content.Text

#     # Закрываем документ и приложение Word
#     doc.Close(False)
#     word.Quit()
#     return text

# Функция для извлечения текста (пример из предыдущих шагов)
def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)  # Используй свою функцию
    if file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)  # Используй свою функцию
    # if file_path.endswith(".doc"):
    #     return extract_text_from_doc(file_path)  # Используй свою функцию
    if file_path.endswith(".html"):
        return extract_text_from_txt(file_path)
    else:
        return ""

def split_text_into_chunks(text, max_tokens=8000):
    # Выбираем токенайзер
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")

    # Преобразуем текст в токены
    tokens = encoding.encode(text)
    
    # Разделяем текст на части
    chunks = []
    while len(tokens) > max_tokens:
        chunk = tokens[:max_tokens]
        chunks.append(encoding.decode(chunk))
        tokens = tokens[max_tokens:]
    chunks.append(encoding.decode(tokens))  # Последний блок
    return chunks

def ask_questions(output_dir, questions):
    # Чтение текста из всех файлов
    files_text = {}

    directory = Path(output_dir)
    files_path = [str(file) for file in Path(directory).rglob('*') if file.is_file()]

    for path in files_path:
        path = str(path)
        text = extract_text_from_file(path)
        file_name = Path(path).name
        if text:  # Пропускаем пустые файлы
            files_text[file_name] = text

    # Объединение текста
    combined_text = ""
    for file_name, text in files_text.items():
        combined_text += f"\n=== Начало текста из файла: {file_name} ===\n"
        combined_text += text
        combined_text += f"\n=== Конец текста из файла: {file_name} ===\n"

    # Разбиваем текст на блоки
    chunks = split_text_into_chunks(combined_text, max_tokens=8000)

    # Укажи свой API-ключ
    openai_key = os.getenv('OpenAI_KEY')
    client = OpenAI(api_key = openai_key)

    # первый абзац в документе с вопросами - promt для ИИ, описывающий что надо сделать
    system_promt = questions[0]
    del questions[0]

    res = ''
    for idx, question in enumerate(questions, 1):
        if(question.strip() == ""):
            continue

        relevant_chunks = []
        print(question)

        # Обрабатываем каждый блок
        for i, chunk in enumerate(chunks, 1):
            #print(f"Обрабатываем блок {i}/{len(chunks)}...")
            
            # Формируем запрос чтобы выделить только блоки, содержащие нужную информацию
            prompt = (
                f"Вот фрагмент текста:\n{chunk}\n\nОтветь содержит ли этот текст ответы на следующие вопросы. Твой ответ должен содержать только Да или Нет. Больше ничего отвечать, детализировать не надо:\n"
                )

            prompt += f"{idx}. {question}\n"

            # Отправляем запрос в OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты сотрудник отдела закупок, который проводит анализ конкурсной документации."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response.choices[0].message.content
            print(answer)
            if "да" in answer.lower():
                relevant_chunks.append(chunk)       

        #Сформировать запрос из релевантных фрагментов:
        combined_relevant_text = "\n".join(relevant_chunks)

        prompt = (
            f"Вот фрагмент текста:\n{combined_relevant_text}\n\nОтветь на следующие вопросы:\n"
            )

        prompt += f"{idx}. {question}\n"

        # Отправляем запрос в OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_promt},
                {"role": "user", "content": prompt}
            ]
        )
        res += f"{idx}. {response.choices[0].message.content}\n<br>"

    return res