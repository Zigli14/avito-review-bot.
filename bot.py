from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import random
import requests
from bs4 import BeautifulSoup
import pickle
import os

app = Flask(__name__)

# Настройки прокси (можно добавить список прокси)
PROXY = "your_proxy:port"  # Укажи свой прокси

# Путь к файлу с куками
COOKIES_FILE = "cookies.pkl"

# Список аккаунтов (можно загрузить из базы данных)
ACCOUNTS = [
    {"login": "your_login1", "password": "your_password1"},
    {"login": "your_login2", "password": "your_password2"}
]

def get_driver():
    """Создаём драйвер с настройками прокси."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск в фоновом режиме
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--proxy-server={PROXY}")  # Если прокси не нужен, удали эту строку
    
    driver = webdriver.Chrome(options=options)
    return driver

def save_cookies(driver):
    """Сохраняем куки после успешного входа."""
    with open(COOKIES_FILE, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver):
    """Загружаем сохраненные куки, если они есть."""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

def login(driver, account):
    """Авторизация с куками или через ввод логина/пароля."""
    driver.get("https://www.avito.ru/")
    time.sleep(random.randint(5, 10))
    
    try:
        load_cookies(driver)
        driver.refresh()
        time.sleep(random.randint(5, 10))
        return "Авторизация через куки выполнена."
    except:
        pass
    
    try:
        login_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Вход')]")
        login_button.click()
        time.sleep(random.randint(3, 7))
        
        login_field = driver.find_element(By.NAME, "login")
        login_field.send_keys(account["login"])
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(account["password"], Keys.RETURN)
        
        time.sleep(random.randint(5, 10))
        save_cookies(driver)
        return "Авторизация через логин/пароль выполнена."
    except NoSuchElementException:
        return "Ошибка авторизации!"

def parse_avito(url):
    """Парсим информацию об объявлении."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find("span", class_="title-info-title-text")
    description = soup.find("div", class_="item-description")
    
    return {
        "title": title.text if title else "Товар",
        "description": description.text if description else "Описание отсутствует"
    }

def generate_review(title, description):
    """Генерация отзыва на основе информации о товаре."""
    templates = [
        f"Купил {title}, очень доволен! {description[:100]}...",
        f"{title} – отличный выбор! Доставка быстрая, качество супер.",
        f"Не ожидал такого качества от {title}, но приятно удивлён!"
    ]
    return random.choice(templates)

def interact_with_ad(driver, url):
    """Совершение целевых действий на объявлении перед публикацией отзыва."""
    driver.get(url)
    time.sleep(random.randint(5, 10))
    
    try:
        # Нажимаем на кнопку 'Показать контакты'
        contact_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Показать контакты')]")
        contact_button.click()
        time.sleep(random.randint(3, 7))
    except NoSuchElementException:
        pass
    
    try:
        # Открываем чат с продавцом
        chat_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Написать')]")
        chat_button.click()
        time.sleep(random.randint(3, 7))
        
        chat_input = driver.find_element(By.CLASS_NAME, "chat-input")
        chat_input.send_keys("Здравствуйте! Интересует ваше предложение.", Keys.RETURN)
        time.sleep(random.randint(3, 7))
    except NoSuchElementException:
        pass

def post_review(driver, url, review_text):
    """Публикация отзыва с обработкой ошибок и защитой от спама."""
    interact_with_ad(driver, url)
    time.sleep(random.randint(5, 10))
    
    driver.get(url)
    time.sleep(random.randint(5, 10))
    
    try:
        review_box = driver.find_element(By.CLASS_NAME, "review-textarea")
        review_box.send_keys(review_text)
        time.sleep(random.randint(2, 5))
        
        submit_button = driver.find_element(By.CLASS_NAME, "submit-button")
        submit_button.click()
        return "Отзыв успешно оставлен!"
    except NoSuchElementException as e:
        return f"Ошибка: элемент не найден ({e})"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    avito_url = request.form['url']
    data = parse_avito(avito_url)
    review = generate_review(data["title"], data["description"])
    
    account = random.choice(ACCOUNTS)
    driver = get_driver()
    auth_message = login(driver, account)
    
    if "Ошибка" in auth_message:
        driver.quit()
        return jsonify({"message": auth_message})
    
    result = post_review(driver, avito_url, review)
    driver.quit()
    
    return jsonify({"message": result})

if __name__ == "__main__":
   gunicorn_app = app
