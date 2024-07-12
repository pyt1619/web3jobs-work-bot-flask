from flask import Flask, render_template, request, redirect, url_for, abort,send_from_directory
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import jsonify
from flask import send_file
from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, SubmitField
from forms import *
from db import *
import os
from flask_cors import CORS
import asyncio
import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, InputFile
from aiogram import Bot, Dispatcher, types
import requests
import uuid, json
from threading import Thread, Lock
from config import *


bot = Bot(token=TOKEN)

app = Flask(__name__)
app.config['SECRET_KEY'] = '07b7855a3b5e298b863cefdcded14a2a0ec2fbac111f6230'  # Замените на свой секретный ключ
app.config['UPLOAD_FOLDER'] = './upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
Bootstrap(app)
CORS(app)

login_manager = LoginManager(app)
bcrypt = Bcrypt()

lock = Lock()

# Пример данных, которые могут быть отображены в админской панели
admin_data = {
    "users": ["User1", "User2", "User3"],
    "posts": ["Post1", "Post2", "Post3"]
}

def send_amplitude_event( user_id, event_type, event_properties=None):
    def send_data(user_id, event_type, event_properties):
        global lock
        url = "https://api.amplitude.com/2/httpapi"
        with lock:
            user_data = get_user_data(user_id)
        registration_date = datetime.strptime(user_data['registration_date'], '%Y-%m-%d')
        cohort_year = registration_date.year
        cohort_month = registration_date.month
        cohort_week = registration_date.isocalendar()[1]  # Получаем номер недели
        cohort_day = registration_date.timetuple().tm_yday  # Получаем номер дня в году
        referral = user_data['ref_id'] if user_data['ref_id'] else ''
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }
        event = {
            "api_key": 'e0d57919c56bbf7e8555c602c3c0dcd5',
            "events": [
                {
                    "user_id": user_id,
                    "event_type": event_type,
                    'event_properties': {
                        'cohort_year': cohort_year,
                        'cohort_month': cohort_month,
                        'cohort_week': cohort_week,
                        'cohort_day': cohort_day,
                        'referral': referral
                    }
                }
            ]
        }
        if event_properties:
            event['events'][0]['event_properties'].update(event_properties)
        response = requests.post(url,headers=headers, data=json.dumps(event))
    t = Thread(target=send_data, args=(user_id, event_type, event_properties))
    t.start()

# Создаем класс пользователя
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_id(self):
        return str(self.id)



# Пример списка пользователей (замените на ваш способ хранения пользователей)
users = {"admin1337": {"username": "admin1337", "password": bcrypt.generate_password_hash("PjRZw44LNVydMdYDj8KXVWwwFzKmljvyKWvL").decode()}}


# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Защищенный роут: проверка аутентификации
def check_auth(username, password):
    user = users.get(username)
    if user and bcrypt.check_password_hash(user["password"], password):
        return User(username)
    return None



# Показать форму входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = check_auth(username, password)

        if user:
            # Вход успешен, установка сессии
            login_user(user)
            return redirect(url_for('admin_panel'))
        else:
            # Неверные учетные данные
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html', error=None)


# Защищенная админская панель
@app.route('/admin')
@login_required
def admin_panel():
    return render_template('admin_panel.html', data=admin_data)

@app.route('/get_data_page_1', methods=['GET', 'POST'])
def get_data_page_1():
    telegram_id=int(request.args.get('telegram_id'))
    send_amplitude_event(telegram_id, 'Onboarding start')
    return jsonify(count_company_and_vacancies())

@app.route('/open_subscribtion', methods=['GET', 'POST'])
def open_subscribtion():
    telegram_id=int(request.args.get('telegram_id'))
    send_amplitude_event(telegram_id, 'Paywall_open')
    return jsonify({'OK':True})

@app.route('/get_site_count_vacancy', methods=['GET', 'POST'])
def get_site_count_vacancy():
    return jsonify(count_company_and_vacancies_and_posted_last_week())

@app.route('/get_user_categories', methods=['GET'])
def get_user_categories_route():
    telegram_id = request.args.get('telegram_id')  # Получение telegram_id из GET-параметра запроса
    send_amplitude_event(telegram_id, 'Onboarding2nd')
    if telegram_id:
        user_categories = get_user_categories(telegram_id)
        return jsonify({'categories': user_categories})
    else:
        return jsonify({'error': 'Missing telegram_id parameter'})



@app.route('/user_statistics')
@login_required
def user_statistics():
    data = get_user_counts()
    return render_template('user_statistics.html', data=data)

@app.route('/get_user_statistics', methods=['GET'])
@login_required
def get_user_statistics():
    start_date=request.args.get('start_date')
    end_date=request.args.get('end_date')
    try:
        data = get_user_counts(start_date, end_date)
    except:
        data = get_user_counts()

    return jsonify(data)


@app.route('/user_payments')
@login_required
def user_payments():
    data = get_payment_statistics_with_details()
    return render_template('user_payments.html', data=data)


@app.route('/promo_month', methods=['GET'])
@login_required
def promo_month():
    telegram_id = request.args.get('telegram_id')
    set_month_promo(telegram_id)
    return redirect(url_for('user_list'))



@app.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    form = UserFilter()
    status=None
    users = get_user_table()
    if form.validate_on_submit():
        paid_year = form.paid_year.data
        paid_monthly = form.paid_monthly.data
        trial = form.trial.data
        promo = form.promo.data
        free = form.free.data

        users=[]
        user_tmp = get_user_table()
        for user in user_tmp:
            if(paid_year and user[4] == 'paid year'):
                users.append([user[1],user[4],user[3],user[2]])
            elif(paid_monthly and user[4] == 'paid monthly'):
                users.append([user[1],user[4],user[3],user[2]])
            elif(trial and user[4] == 'trial'):
                users.append([user[1],user[4],user[3],user[2]])
            elif(promo and user[4] == 'promo'):
                users.append([user[1],user[4],user[3],user[2]])
            elif(free and user[4] == 'not paid'):
                users.append([user[1],user[4],user[3],user[2]])

    else:
        users=[]
        user_tmp = get_user_table()
        for user in user_tmp:
            users.append([user[1],user[13],user[4],user[3],user[2]])


    return render_template('user_list.html', form=form, users=users)

@app.route('/download_parser_log', methods=['GET', 'POST'])
@login_required
def download_log():
    log_file = 'parser_log.txt'
    if os.path.exists(log_file):
        return send_file(log_file, as_attachment=True)
    else:
        return jsonify({'error': 'Log file not found'}), 404


@app.route('/write_to_users', methods=['GET', 'POST'])
@login_required
def write_to_users():
    form = SendMsgForm()
    status=None
    if form.validate_on_submit():
        paid_year = form.paid_year.data
        paid_monthly = form.paid_monthly.data
        trial = form.trial.data
        promo = form.promo.data
        free = form.free.data
        msg = form.msg.data
        image_path = ''
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                image_path = filename

        if(msg.strip() == ''):
            status = 'текст сообщения пустой'
        else:
            status = 'Сообщение отправленно'
            add_message(paid_year, paid_monthly, trial, promo, free, msg, image_path)
            form.paid_year.data = False
            form.paid_monthly.data = False
            form.trial.data = False
            form.promo.data = False
            form.free.data = False
            form.msg.data = ''
            form.image.data=None

    return render_template('write_to_users.html', form=form,status=status)


@app.route('/all_vacancies', methods=['GET'])
@login_required
def all_vacancies():
    category_filter_form = CategoryFilterForm(request.args)
    if category_filter_form.submit_category_filter.data:
        # Обработка выбранных категорий и применение фильтрации
        title_search = category_filter_form.title_search.data
        company_search = category_filter_form.company_search.data
        print(f'###{company_search}###')
        selected_categories = []
        if category_filter_form.category_customer_support.data:
            selected_categories.append('Customer Support')
        if category_filter_form.category_design.data:
            selected_categories.append('Design')
        if category_filter_form.category_technical.data:
            selected_categories.append('Technical')
        if category_filter_form.category_finance.data:
            selected_categories.append('Finance')
        if category_filter_form.category_marketing.data:
            selected_categories.append('Marketing')
        if category_filter_form.category_nontech.data:
            selected_categories.append('Non-Tech')
        if category_filter_form.category_operations.data:
            selected_categories.append('Operations')
        if category_filter_form.category_product_surin.data:
            selected_categories.append('Product Surin')
        if category_filter_form.category_other.data:
            selected_categories.append('Other')

        # Реализуйте фильтрацию вакансий в базе данных или другом источнике данных
        if selected_categories:
            pass
        vacancies_data = create_table_xlsx(title_search, company_search, selected_categories, return_array=True)


        return send_file('out.xlsx', as_attachment=True)

    return render_template('all_vacancies.html',  category_filter_form=category_filter_form)


@app.route('/parser_report')
@login_required
def parser_report():
    return render_template('parser_report.html')

@app.route('/referral_statistics')
@login_required
def referral_statistics():
    data = get_daily_statistics()
    return render_template('referral_statistics.html', data=data)

@app.route('/get_referral_statistics', methods=['GET'])
@login_required
def get_referral_statistics():
    start_date=request.args.get('start_date')
    end_date=request.args.get('end_date')
    try:
        data = get_daily_statistics(start_date, end_date)
    except:
        data = get_daily_statistics()

    return jsonify(data)


@app.route('/all_promoters', methods=['GET'])
@login_required
def all_promoters():
    telegram_id = request.args.get('telegram_id')
    if(telegram_id):
        data = get_referral_promoters_count(telegram_id)
        return render_template('all_promoters.html', data=data, search=telegram_id)
    else:
        data = get_referral_promoters_count()
        return render_template('all_promoters.html', data=data, search='')


@app.route('/referral_leads', methods=['GET'])
@login_required
def referral_leads():
    telegram_id = request.args.get('telegram_id')

    if(telegram_id):
        data = get_referral_payments(telegram_id)
        return render_template('referral_leads.html', data=data, search=telegram_id)
    else:
        data = get_referral_payments()
        return render_template('referral_leads.html', data=data, search='')

@app.route('/update_transaction_id', methods=['POST'])
@login_required
def update_transaction_id():
    data = request.json
    transaction_id = data.get('id')
    new_transaction_id = data.get('transaction_id')
    if transaction_id is not None and new_transaction_id is not None:
        if update_transaction_id_by_id(transaction_id, new_transaction_id):
            transaction = get_transaction_info(transaction_id)
            asyncio.run(send_msg(transaction['telegram_id'], f"Your payment of {transaction['amount']} usdt has been made!\n\nTransaction link: <a href='https://tronscan.org/#/transaction/{transaction['transaction_id']}'>link</a>"))
            return jsonify({"message": "Transaction ID updated successfully"}), 200
        else:
            return jsonify({"error": "Transaction ID not found"}), 404
    else:
        return jsonify({"error": "Invalid request"}), 400

@app.route('/payout_requests')
@login_required
def payout_requests():
    transactions = get_transactions_without_id()
    return render_template('payout_requests.html', data = transactions)

@app.route('/payout_statistics')
@login_required
def payout_statistics():
    # https://usdt.tokenview.io/ru/tx/0x593cb5ed59b260b85a66325a7dd191b6f434280b4a65850926d557808fd83f9f
    transactions = get_transactions_with_id()
    return render_template('payout_statistics.html', data=transactions)


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


async def send_msg(telegram_id, msg):
    await bot.send_message(telegram_id, msg, parse_mode='HTML')

async def send_start_msg(telegram_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    user = get_user_data(telegram_id)
    if(user['subscription_type'] == 'free'):
        markup.add(types.InlineKeyboardButton(text="🔓 Get access!", web_app=WebAppInfo(url=f'https://web3jobs.online/start.html')))
    elif(user['subscription_type'] == 'no paid'):
        markup.add(types.InlineKeyboardButton(text="👛 Buy paid access now!", web_app=WebAppInfo(url=f'https://web3jobs.online/subscribtion.html')))
    else:
        markup.add(types.InlineKeyboardButton(text="👁 View jobs", web_app=WebAppInfo(url=f'https://web3jobs.online/jobs.html')))
        if(user['subscription_type'] == 'trial'):
            markup.add(types.InlineKeyboardButton(text="👛 Buy paid access now!", web_app=WebAppInfo(url=f'https://web3jobs.online/subscribtion.html')))

    markup.add(types.InlineKeyboardButton(text="👋🏻 Referral program", callback_data="reflink"))
    markup.add(types.InlineKeyboardButton(text="⚙️ Settings", callback_data="job_settings"))
    count = count_company_and_vacancies()

    if(user['subscription_type'] != 'free'):
        # await bot.send_message(telegram_id, f'<b>{count["total_vacancies"]} jobs</b> from <b>{count["unique_company"]} companies</b>.\nClick on the "<i>👁 View Jobs</i>" button or customize your job display by changing categories, keywords, or specific company names.', reply_markup=markup, parse_mode='HTML')
        await bot.send_message(telegram_id, f'Total number of job openings in bot:\n<b>{count["total_vacancies"]} jobs from {count["unique_company"]} companies.</b>\nClick on the "👁 View Jobs" button or customize your job display by changing categories, keywords, or specific company names.', reply_markup=markup, parse_mode='HTML')
    else:
        await bot.send_message(telegram_id, '👋🏻 Welcome to the Web3 Jobs Bot!\n\n<b>This bot is the best place for professionals looking for web3 jobs!</b>\n\n👀 We monitor companies that have received investments from web3-focused venture capital funds, as well as funds from major crypto ecosystems.\n\n💼 With the help of the bot, you will be able to browse job offers in the professions you are interested in, as well as receive notifications when new job offers appear. Use our bot as an indispensable tool to find your dream job on web3!', reply_markup=markup, parse_mode='HTML')




@app.route('/receive_categories', methods=['POST'])
def receive_categories():
    data = request.get_json()

    categories = data.get('categories', [])
    telegram_id = data.get('telegram_id')
    categories = ', '.join(categories)
    print('Received categories:', categories)
    print('Received telegram_id:', telegram_id)

    update_user_parameter(telegram_id, 'category', categories)
    if(categories.strip() != ''):
        asyncio.run(send_msg(telegram_id, 'Selected categories: ' + categories))
    else:
        asyncio.run(send_msg(telegram_id, 'Categories selected: none'))

    return jsonify({'success': True, 'message': 'Categories received successfully'})


@app.route('/extend_subscription', methods=['POST'])
def extend_subscription():
    data = request.get_json()
    telegram_id = data.get('telegram_id')

    user = get_user_data(telegram_id)
    print(telegram_id)
    if 'subscription_type' in user['subscription_type']:
        if user['subscription_type'] != 'free':
            return jsonify({'success': False, 'message': 'User already on trial subscription'})

    if user['subscription_end_date'] == None or user['subscription_end_date'] == '':
        current_date = datetime.now()
        new_date = current_date + timedelta(days=5)
        new_date = new_date.strftime("%Y-%m-%d")
    else:
        subscription_end_date = user['subscription_end_date']
        date_obj = datetime.strptime(subscription_end_date, "%Y-%m-%d")
        new_date_obj = date_obj + timedelta(days=5)
        new_date = new_date_obj.strftime("%Y-%m-%d")

    update_user_parameter(telegram_id, 'subscription_end_date', new_date)
    update_user_parameter(telegram_id, 'subscription_type', 'trial')
    asyncio.run(send_msg(telegram_id, '<b>🎉 Your 5-day trial is activated!</b>'))
    asyncio.run(send_start_msg(telegram_id))
    send_amplitude_event(telegram_id, 'Trial_start')


    return jsonify({'success': True, 'message': 'Subscription extended successfully'})

@app.route('/create_payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    amount = data.get('amount')
    external_id = str(uuid.uuid4())


    created_order = create_order(
        amount=f"{amount}",
        currency_code="USD",
        description="Web3 Jobs Bot",
        return_url=f'https://t.me/jobs_web3_bot',
        fail_return_url=f'https://t.me/wallet',
        external_id = external_id,
        timeout_seconds=10800,
        customer_telegram_user_id=telegram_id
    )
    add_payment(amount, external_id, telegram_id, payment_id=None)

    payment_link = created_order.get('data', {}).get('payLink')
    return jsonify({'success': True, 'payment_link': payment_link})

def create_order(amount, currency_code, description, return_url, fail_return_url, external_id, timeout_seconds, customer_telegram_user_id):
    url = "https://pay.wallet.tg/wpay/store-api/v1/order"
    headers = {
        "Content-Type": "application/json",
        "Wpay-Store-Api-Key": API_KEY
    }
    payload = {
        "amount": {
            "currencyCode": currency_code,         # Валюта заказа
            "amount": amount                       # Сумма заказа
        },
        "description": description,                 # Описание заказа
        "returnUrl": return_url,                    # URL для перенаправления после успешной оплаты
        "failReturnUrl": fail_return_url,           # URL для перенаправления после неудачной оплаты
        "externalId": external_id,                  # Внешний идентификатор заказа
        "timeoutSeconds": timeout_seconds,          # Время жизни заказа в секундах
        "customerTelegramUserId": customer_telegram_user_id  # ID пользователя Telegram (необходим для создания заказа)
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json() if response.status_code == 200 else None

@app.route('/tgwallet/ipn', methods=['POST'])
def ipn_tgwallet():

    for event in request.get_json():
        if event["type"] == "ORDER_PAID":
            data = event["payload"]
            if(is_payment_successful(data['id'])):
                telegram_id=set_payment_date(data["externalId"])
                amount = data['orderAmount']['amount']
                if(amount == 20):
                    days = 30
                    send_amplitude_event(telegram_id, 'Payment_complete', {'payment_type':'Monthly'})
                else:
                    days=365
                    send_amplitude_event(telegram_id, 'Payment_complete', {'payment_type':'annual'})

                user = get_user_data(telegram_id)
                if(user['subscription_end_date']==None or user['subscription_end_date']==''):
                    current_date = datetime.now()
                    new_date = current_date + timedelta(days=days)
                    new_date = new_date.strftime("%Y-%m-%d")
                else:
                    subscription_end_date = user['subscription_end_date']
                    date_obj = datetime.strptime(subscription_end_date, "%Y-%m-%d")
                    new_date_obj = date_obj + timedelta(days=days)
                    new_date = new_date_obj.strftime("%Y-%m-%d")

                update_user_parameter(telegram_id, 'subscription_end_date', new_date)
                update_user_parameter(telegram_id, 'last_subscription_date', new_date)

                if(user['ref_id'] or user['ref_id']!=''):
                    ref_data = get_user_data(user['ref_id'])
                    add_ref_sum = eval(f"{ref_data['balance']}+{amount}/2")
                    update_user_parameter(user['ref_id'], 'balance', add_ref_sum)
                    if(ref_data['notification'] == 1):
                        asyncio.run(send_msg(user['ref_id'], f'Your account has received {add_ref_sum} usdt because one of your referrals made a new payment.'))



                update_user_parameter(telegram_id, 'subscription_type', 'paid')
                asyncio.run(send_msg(telegram_id, f"<b>🎉 Thanks for paying!</b>\n\nWeb3 Jobs Bot paid until {new_date}\nYou can browse jobs by category or search by keyword or by company name.\n\nDon't forget to customize your alerts so you never miss a job."))

    return 'OK'


def is_payment_successful(order_id):
    # URL для получения информации о заказе
    url = f"https://pay.wallet.tg/wpay/store-api/v1/order/preview?id={order_id}"
    # Заголовки запроса
    headers = {
        "Wpay-Store-Api-Key": API_KEY
    }
    # Отправка GET-запроса для получения информации о заказе
    response = requests.get(url, headers=headers)
    # Проверка статуса ответа
    if response.status_code == 200:
        # Получение данных из JSON-ответа
        data = response.json().get("data")
        if data:
            # Проверка статуса оплаты
            payment_status = data.get("status")
            if payment_status == "PAID":
                return True
            else:
                return False
        else:
            return False
    else:
        return False




import sqlite3


@app.route('/get_count_vacancies', methods=['GET'])
def get_count_vacancies():
    telegram_id = request.args.get('telegram_id')
    user_data = get_user_data(telegram_id)
    result = int(request.args.get('result'))
    if(result==1):
        send_amplitude_event(telegram_id, 'Onboarding3rd')
    else:
        send_amplitude_event(telegram_id, 'Look_jobs')


    connection = sqlite3.connect('vacancies.db')
    cursor = connection.cursor()

    # Создаем пустые списки для ключевых слов, компаний и категорий
    keywords_conditions = []
    companies_conditions = []
    categories_conditions = []

    # Разбиваем строки на списки и удаляем лишние пробелы
    keywords_list = [keyword.strip() for keyword in user_data['keywords'].split(',') if keyword.strip()]
    companies_list = [company.strip() for company in user_data['companies'].split(',') if company.strip()]
    categories_list = [category.strip() for category in user_data['category'].split(',') if category.strip()]

    # Формируем условия для запроса на основе списков
    if keywords_list:
        keywords_conditions = ["job_title LIKE ?" for _ in range(len(keywords_list))]

    if companies_list:
        companies_conditions = ["company_name LIKE ?" for _ in range(len(companies_list))]

    if categories_list:
        categories_conditions = ["categories LIKE ?" for _ in range(len(categories_list))]

    # Формируем запрос и параметры для запроса
    count_query = 'SELECT COUNT(job_title) AS job_count, COUNT(DISTINCT company_name) AS company_count FROM vacancies WHERE id != ?'

    conditions = " OR ".join(keywords_conditions + companies_conditions + categories_conditions)

    count_params_query = (0,) + tuple(f"%{keyword}%" for keyword in keywords_list + companies_list + categories_list)
    if conditions:
        count_query += f" AND ({conditions})"
    print(count_query, count_params_query)
    cursor.execute(count_query, count_params_query)
    counts = cursor.fetchone()

    connection.close()

    # Возвращаем только количество вакансий и компаний
    job_count, company_count = counts

    # Преобразуйте данные в формат JSON и верните их
    return jsonify({'job_count': job_count, 'company_count': company_count})




@app.route('/get_vacancies', methods=['GET'])
def get_vacancies():


    page = request.args.get('page', default=1, type=int)
    telegram_id = request.args.get('telegram_id')
    user_data = get_user_data(telegram_id)
    if(user_data['subscription_type'] in ['free', 'no paid']):
        return jsonify({'vacancies': []})

    per_page = 10

    connection = sqlite3.connect('vacancies.db')
    cursor = connection.cursor()

    # Создаем пустые списки для ключевых слов, компаний и категорий
    keywords_conditions = []
    companies_conditions = []
    category_conditions = []

    # Разбиваем строки на списки и удаляем лишние пробелы
    keywords_list = [keyword.strip() for keyword in user_data['keywords'].split(',') if keyword.strip()]
    companies_list = [company.strip() for company in user_data['companies'].split(',') if company.strip()]
    category_list = [category.strip() for category in user_data['category'].split(',') if category.strip()]

    # Формируем условия для запроса на основе списков
    if keywords_list:
        keywords_conditions = ["job_title LIKE ?" for _ in range(len(keywords_list))]

    if companies_list:
        companies_conditions = ["company_name LIKE ?" for _ in range(len(companies_list))]

    if category_list:
        category_conditions = ["categories LIKE ?" for _ in range(len(category_list))]

    # Формируем запрос и параметры для запроса
    query = 'SELECT * FROM vacancies WHERE id != ?'

    conditions = " OR ".join(keywords_conditions + companies_conditions + category_conditions)

    params_query = (0,) + tuple(f"%{keyword}%" for keyword in keywords_list + companies_list + category_list)

    if conditions:
        query += f" AND ({conditions})"

    query += ' ORDER BY employer_posted_date DESC LIMIT ? OFFSET ?'

    params_query += (per_page, (page - 1) * per_page)

    cursor.execute(query, params_query)
    vacancies = cursor.fetchall()

    connection.close()

    return jsonify({'vacancies': vacancies})


@app.route('/vizitka/<path:filename>')
def vizitka_f(filename):
    return send_from_directory('templates/site', filename)

# Настройка пути для статических файлов для второй страницы
@app.route('/vizitka')
def vizitka():
    return render_template('site/index.html')


@app.route('/<path:link>')
def display_html(link):

    html_path = f'./dist/{link}'
    # Проверка наличия файла и отображение
    return send_from_directory('templates/dist', link)

     # if os.path.exists(html_path) else  abort(404)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8085, ssl_context=('/home/admin/conf/web/web3jobs.online/ssl/web3jobs.online.pem', '/home/admin/conf/web/web3jobs.online/ssl/web3jobs.online.key'))
