import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs

from gigachat import GigaChat
from gigachat.exceptions import AuthenticationError
from gigachat.models import Chat, Messages, MessagesRole

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
    }

cpar = {
    "[": "]",
    "(": ")",
    "{": "}",
    "<": ">",
    }

def get_api_key():
    with open("api_key.txt") as f:
        return f.read()

def delete_parenthesis(text, par = "["):
    if par not in text:
        return text

    low = text.find(par)
    up = text.find(cpar[par]) + 1

    return delete_parenthesis(text[:low] + text[up:], par)
    

def parse_raw_text(link: str) -> str:
    global headers

    response = requests.get(link, headers)
    response.raise_for_status()
    print(f"Got {link}")
    
    soup = bs(response.text, "html.parser")

    return soup.get_text()

def parse_all_links(forced=False):
    
    with open("relevant_links.txt") as f:
        links = [line[:-1] for line in f.readlines()]
        
    for index, link in enumerate(links):
        filename = link[16:].replace("/"," ") + ".txt"
        if not forced and filename in os.listdir("parsed"):
            print(f"Skipped {link}")
            continue

        text = ""
        try:
            text = parse_raw_text(link)
            if index != len(list) - 1:
                time.sleep(2)
            
        except Exception as e:
            print(f"Failed to parse {link}: ", e)

        if text:
            with open(os.path.join("parsed", filename), "w", encoding='utf-8') as f:
                f.write(delete_parenthesis(text))

def remove_junk_text(text: str):
    with open("junk.txt", encoding="utf-8") as j:
        junk = j.read()
        
    text = text.replace(junk, "")
    
    return text[:text.find("Напишите нам   Отправить")]

def get_text(stop=-1):
    text = ""
    
    for i, filename in enumerate(os.listdir("parsed")):
        with open(os.path.join("parsed", filename), encoding="utf-8") as f:
            text += remove_junk_text(f.read())
                  
        if i == stop:
            return text
        
    return " ".join(text.split())

def main() -> None:
    print("EORA test AI manager made by T. Malkov\n\n")

    giga = GigaChat(credentials=get_api_key())
    
    while True:
        input_ = input("\nВыберите действие (введите цифру):\n 1. Задать вопрос\n"
                       " 2. Посмотреть системный промпт\n"
                       " 3. Обновить информацию с соответствующих ссылок\n"
                       " 4. Принудительно обновить информацию с соответствующих ссылок\n"
                       " 5. Выйти\n\n")

        if input_ == "1":
            with open("prompt.txt", encoding="utf-8") as f:
                prompt = f.read()
                
            text = get_text()
            question = input("Введите ваш вопрос: ")

            chat = Chat(
                messages=[
                    Messages(
                        role=MessagesRole.SYSTEM,
                        content=prompt.format(text),
                        ),
                    Messages(
                        role=MessagesRole.USER,
                        content=question,
                        ),
                    ]
                )
            try:
                response = giga.chat(chat)
                print(response.choices[0].message.content + "\n")

            except AuthenticationError:
                print("\nНеверный API ключ в файле api_key.txt")

        elif input_ == "2":
            print(get_text())
        
        elif input_ == "3":
            parse_all_links()
        
        elif input_ == "4":
            parse_all_links(True)
        
        elif input_ == "5":
            break

        else:
            print("Введено неверное число")

if __name__ == "__main__":
    main()






























