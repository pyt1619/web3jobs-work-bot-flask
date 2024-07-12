import undetected_chromedriver as uc
from time import sleep
import pickle 
import time, random
import json,sys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from ftfy import fix_encoding
import natsort
from db import *
import asyncio
from aiogram import Bot, Dispatcher, types
from config import *
import logging
from datetime import datetime
from pyvirtualdisplay import Display

# Создаем виртуальный дисплей
display = Display(visible=0, size=(1920, 1080))
display.start()
version_main=124
# version_main=121



# Configure logging
logging.basicConfig(filename='parser_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

bot = Bot(token=TOKEN)

class Getro():
    def __init__(self):
        self.driver = None
        self.urls = [
                "https://careers.animocabrands.com/jobs",
                "https://careers.zilliqa.com/jobs",
                "https://careers.alephzero.org/jobs",
                "https://jobs.algorand.foundation/jobs",
                "https://jobs.coinfund.io/jobs",
                "https://jobs.bnbchain.org/jobs",
                "https://borderlesscapital.getro.com/jobs",
                "https://careers.mesh.xyz/jobs",
                "https://jobs.dragonfly.xyz/jobs",
                "https://d1.getro.com/jobs",
                "https://coinbase.getro.com/jobs",
                "https://jobs.polychain.capital/jobs",
                "https://variant.getro.com/jobs",
                "https://jobs.multicoin.capital/jobs",
                "https://jobs.blockchaincapital.com/jobs",
                "https://jobs.electriccapital.com/jobs",
                "https://hivemindcapital.getro.com/jobs",
                "https://jobs.framework.ventures/jobs",
                "https://jobs.placeholder.vc/jobs",
                "https://jobs.collabcurrency.com/jobs",
                "https://jobs.dcg.co/jobs",
                "https://jobs.baincapitalcrypto.com/jobs",
                "https://jobs.delphiventures.io/jobs",
                "https://jobs.outlierventures.io/jobs",
                "https://circleventures.getro.com/jobs",
                "https://jobs.paradigm.xyz/jobs",
                "https://jobs.ton.org/jobs",
                "https://jobs.optimism.io/jobs",
                "https://jobs.solana.com/jobs",
                "https://careers.near.org/jobs",
                "https://careers.substrate.io/jobs",
                "https://jobs.arbitrum.io/jobs",
                "https://jobs.sui.io/jobs",
                "https://jobs.jumpcap.com/jobs",
                "https://jobs.spartangroup.io/jobs",
                "https://jobs.coinfund.io/jobs",
                "https://careers.bitkraft.vc/jobs?filter=eyJvcmdhbml6YXRpb24uaW5kdXN0cnlfdGFncyI6WyJCbG9ja2NoYWluIGFuZCBDcnlwdG8iXX0%3D",
                "https://jobs.foresightventures.com/jobs?filter=eyJvcmdhbml6YXRpb24uaW5kdXN0cnlfdGFncyI6WyJCbG9ja2NoYWluIGFuZCBDcnlwdG8iXX0%3D",
                "https://careers.rarestone.capital/jobs?filter=eyJvcmdhbml6YXRpb24uaW5kdXN0cnlfdGFncyI6WyJCbG9ja2NoYWluIGFuZCBDcnlwdG8iXX0%3D",
                "https://jobs.signum.capital/jobs",
                "https://careers.arkstream.capital/jobs",
                "https://careers.race.capital/jobs",
                "https://jobs.nascent.xyz/jobs",
                "https://jobs.boost.vc/jobs?filter=eyJvcmdhbml6YXRpb24uaW5kdXN0cnlfdGFncyI6WyJCbG9ja2NoYWluIGFuZCBDcnlwdG8iXX0%3D",
            ]
        self.vacancy_urls=[]

    def run(self):
        self.driver = self.new_driver()
        for i in self.urls:
            total_vacancies = 0
            new_vacancies = 0
            new_vacancies_links = []
            try:
                self.driver.get(i)
                try:
                    self.driver.find_element(By.XPATH, '//button[@data-testid="load-more"]').click()
                except:
                    pass
                vacancies = self.load_all()
                total_vacancies = len(vacancies)
                for vacancy in vacancies:
                    if self.get_vacancy_data(vacancy):
                        new_vacancies += 1
                        new_vacancies_links.append(vacancy.find_element(By.XPATH, './/a[@data-testid="job-title-link"]').get_attribute("href"))
            except Exception as e:
                logging.error(f"Error processing URL {i}: {e}")
            finally:
                log_info = f"URL: {i}, Script: Getro, Total Vacancies: {total_vacancies}"
                logging.info(log_info)


    def new_driver(self):
        global driver,version_main 
        try:
            self.driver.quit()
        except:
            pass
        try:
            self.driver.close()
        except:
            pass
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.headless=False
        options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
        self.driver = uc.Chrome(options=options, version_main=version_main) 
        return self.driver

    def load_all(self):
        old_len = 0
        count=5
        while True:
            try:
                self.driver.execute_script("window.scrollTo(0, 20000000000)")
                sleep(2)
                new_len = len(self.driver.find_elements(By.XPATH,'//div[@data-testid="job-list-item"]'))
                if(new_len == 0):
                    return None
                if(count <= 0 and new_len == old_len):
                    return self.driver.find_elements(By.XPATH,'//div[@data-testid="job-list-item"]')
                if(new_len > old_len):
                    old_len=new_len
                    count = 3
                    continue
                if(new_len == old_len):
                    count-=1
            except:
                count-=1
                if(count <= 0):
                    return None


    def get_vacancy_data(self, vacancy):
        try:
            current_url = self.driver.current_url
            title = vacancy.find_element(By.XPATH, './/div[@itemprop="title"]').text
            if title in ['Don’t see what you’re looking for?', "Don't see the right role for you? Apply here!"]:
                return False
            href = vacancy.find_element(By.XPATH, './/a[@data-testid="job-title-link"]').get_attribute("href")
            organization = vacancy.find_element(By.XPATH, './/div[@itemprop="hiringOrganization"]').text
            datePosted = vacancy.find_element(By.XPATH, './/meta[@itemprop="datePosted"]').get_attribute("content")
            url = '/'.join(href[-4:])
            if(url not in self.vacancy_urls):
                add_vacancy(title, href, organization, current_url, datePosted)
                log_info = f"new vacancy {title, href, organization, current_url, datePosted}"
                logging.info(log_info)
                self.vacancy_urls.append(url)

            return True
        except Exception as e:
            logging.error(f"Error getting vacancy data: {e}")
            return False





class Consider():
    def __init__(self):
        self.driver = None
        self.urls = [
            "https://jobs.hashed.com/jobs",
            "https://jobs.sequoiacap.com/jobs?markets=Crypto&markets=Blockchain&markets=FinTech+%26+Blockchain",
            "https://careers.gumi-cryptos.com/jobs",
            "https://jobs.usv.com/jobs?markets=Web3"
        ]
        self.urls2 = [
            "https://jobs.chapterone.com/jobs",
            "https://jobs.panteracapital.com/jobs",
            "https://portfoliojobs.jumpcrypto.com/jobs",
            "https://portfoliojobs.a16z.com/jobs?markets=Web3",
            "https://careers.fenbushicapital.vc/jobs",
            "https://jobs.shima.capital/jobs?markets=Blockchain&markets=Web3&markets=DeFi",
            "https://careers.griffingp.com/jobs?markets=Web3&markets=Blockchain&markets=Layer+1&markets=NFT",
            "https://jobs.protagonist.co/jobs"
        ]


    def load_all(self):
        old_len = 0
        count=3
        while True:
            try:
                self.driver.execute_script("window.scrollTo(0, 20000000000)")
                sleep(2)
                new_len = len(self.driver.find_elements(By.XPATH,'//div[@class="job-list-job-details"]'))
                if(count <= 0 and new_len == old_len):
                    return self.driver.find_elements(By.XPATH,'//div[@class="job-list-job-details"]')
                if(new_len > old_len):
                    old_len=new_len
                    count = 3
                    continue
                if(new_len == old_len):
                    count-=1
            except:
                pass

    def get_all_vakansy(self, current_url):
        self.load_all()
        jobs = self.driver.find_elements(By.XPATH, '//div[@class="job-list-job-details"]')
        organization = self.driver.find_element(By.XPATH, '//h1').text
        for job in jobs:
            try:
                title = job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]').text
                href = job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]/a').get_attribute("href")
                datePosted = job.find_element(By.XPATH, './/span[@class="job-list-badge-text"]').text

                if 'Work remotely' == datePosted:
                    try:
                        datePosted = job.find_elements(By.XPATH, './/span[@class="job-list-badge-text"]')[1].text
                    except:
                        return
                if title == "Don't see the right role for you? Apply here!":
                    return

                add_vacancy(title, href, organization, current_url, datePosted)
            except Exception as e:
                logging.error(f"Error getting all vacancies: {e}")



    def get_vakansy(self, job):
        try:
            current_url = self.driver.current_url
            try:
                organization = job.find_element(By.XPATH,'.//a[@class="job-list-job-company-link"]').text
            except:
                organization = self.driver.find_element(By.XPATH, '//h1').text.replace('Careers at ', '')
            title = job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]').text
            href = job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]/a').get_attribute("href")
            datePosted = job.find_element(By.XPATH, './/span[contains(@class,"job-list-badge-text") and contains(text(), "osted")]').text if 'osted' in job.text else ''
            if('Work remotely' == datePosted):
                try:
                    datePosted = job.find_elements(By.XPATH, './/span[@class="job-list-badge-text"]')[1].text
                except:
                    pass
            if(title == "Don't see the right role for you? Apply here!"):
                return
            add_vacancy(title, href, organization, current_url, datePosted)        
            log_info = f"new vacancy {title, href, organization, current_url, datePosted}"
            logging.info(log_info)
        except Exception as e:
            logging.error(f"Error getting vacancy: {e}")

    def run(self):
        self.driver = self.new_driver()
        for url in self.urls:
            total_vacancies = 0
            new_vacancies = 0
            new_vacancies_links = []
            try:
                self.driver.get(url)
                self.load_all()
                companies = [i.get_attribute("href") for i in self.driver.find_elements(By.XPATH, '//div[@class="grouped-job-result-header"]/a')]
                for company in companies:
                    self.driver.get(company)
                    self.get_all_vakansy(url)
                    total_vacancies += len(self.driver.find_elements(By.XPATH, '//div[@class="job-list-job-details"]'))
                    new_vacancies += sum([self.get_vakansy(job) for job in self.driver.find_elements(By.XPATH, '//div[@class="job-list-job-details"]')])
                    new_vacancies_links.extend([job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]/a').get_attribute("href") for job in self.driver.find_elements(By.XPATH, '//div[@class="job-list-job-details"]')])
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
            finally:
                log_info = f"URL: {url}, Script: Consider, Total Vacancies: {total_vacancies}"
                logging.info(log_info)

        for url in self.urls2:
            total_vacancies = 0
            new_vacancies = 0
            new_vacancies_links = []
            try:
                self.driver.get(url)
                self.load_all()
                organization = self.driver.find_element(By.XPATH, '//h1').text.replace('Careers at ', '')
                jobs = self.driver.find_elements(By.XPATH, '//div[@class="job-list-job-details"]')
                total_vacancies = len(jobs)
                for job in jobs:
                    if self.get_vakansy(job):
                        new_vacancies += 1
                        new_vacancies_links.append(job.find_element(By.XPATH, './/h2[@class="job-list-job-title"]/a').get_attribute("href"))
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
            finally:
                log_info = f"URL: {url}, Script: Consider, Total Vacancies: {total_vacancies}, New Vacancies: {new_vacancies}, New Vacancies Links: {new_vacancies_links}"
                logging.info(log_info)

        try:
            self.driver.quit()
        except:
            pass
        try:
            self.driver.close()
        except:
            pass


    def new_driver(self):
        global driver,version_main 
        try:
            self.driver.quit()
        except:
            pass
        try:
            self.driver.close()
        except:
            pass
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.headless=False
        options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
        self.driver = uc.Chrome(options=options, version_main=version_main) 
        return self.driver


async def parser_out():
    create_table_db('vacancies_new.db')
    if(sum(department['count'] for department in count_new_vacancies_by_category().values()) == 0):
        return
    users = get_users_new_vacancies()
    try:
        users = get_users_new_vacancies()
    except:
        return
    for user in users:
        asyncio.create_task(send_new_vacancy_msgs(user))
    if os.path.exists('vacancies.db'):
        os.remove('vacancies.db')
    if os.path.exists('vacancies_new.db'):
        os.rename('vacancies_new.db', 'vacancies.db')
    create_table()

async def send(user, vacancy):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text="👀View job", url=f'{vacancy["url"]}'))
    markup.add(types.InlineKeyboardButton(text="🔔 Notification settings", callback_data="notification"))
    await bot.send_message(user['id'],  f'<b>🔔 A new job opening for you! 🔔</b>\n\n{vacancy["title"]} at {vacancy["company"]}.', reply_markup=markup, parse_mode="HTML")

async def send_new_vacancy_msgs(user):
    max_count = -1
    for vacancy in user['vacancies']:
        # try:
        try:
            await send(user, vacancy)
        except:
            pass
        # except:
        #     break
        await asyncio.sleep(2)
        max_count-=1
        if(max_count==0):
            break
        if(max_count%10 == 0):
            if get_user_data(user['id'])['notification'] == 0:
                break



# asyncio.run(parser_out())

while True:
    try:
        getro = Getro()
        getro.run()
    except Exception as e:
        print(e)
    try:
        consider = Consider()
        consider.run()
    except Exception as e:
        print(e)
    
    asyncio.run(parser_out())
    sleep(600)
    exit(1)
