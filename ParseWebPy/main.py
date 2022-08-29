

import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from classes import DivInfo
from parseCsv import get_data_from_csv

#боевая ссылка на залогиненный кабинет и открытую декларацию
link = "https://lkfl2.nalog.ru/"
DEBUG = False

def test_func(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")

    browser = webdriver.Chrome(options= options)
    time.sleep(1.0)
    browser.get(url)
    elem = browser.find_element_by_name("text")
    print("1", elem)
    time.sleep(5)
    elem.send_keys("http://программист.рф/" )
    time.sleep(2)
    elem.send_keys(Keys.ENTER)
    
    ac = ActionChains(browser)
    ac.move_to_element(elem)
    ac.click(elem)
    ac.perform()
    time.sleep(3)


def login(browser):
    input('Нажмите Enter чтобы loggining....')
    print("loginning...")

    ref = browser.find_element_by_xpath("//a[@href='/auth/oauth/esia']").click()

    time.sleep(0.5)

    tel = browser.find_element_by_id("login")
    tel.clear()
    tel.send_keys("YOUR TELEPHONE") #INSERT Telephone number +7XXXYYYNNMM
    
    time.sleep(0.3)

    pswd = browser.find_element_by_id("password")
    pswd.clear()
    pswd.send_keys("YOUR PASS" + Keys.ENTER)  #INSERT Password  
    print("OK")

    time.sleep(0.3)
    
def get_cnt_dohod_1(browser):
    cnt_d = 0
    for x in range(32000): #поиск всех источников дохода (записей/строк)
        try: 
            obj = browser.find_element_by_id('Ndfl3Package.payload.sheetB.sources['+str(x)+'].incomeSourceName')
            cnt_d +=1
        except Exception as e:
            break
    return cnt_d

def get_cnt_dohod_2(browser):
    try:
        out_d =  browser.find_element_by_id('react-tabs-3')
        names = out_d.find_elements_by_xpath("//*[contains(text(), 'Наименование *')]") # поиск всех источников дохода по 
    except Exception as e:        
        return 0

    return len(names)

def set_value_to_cmbbox(browser, elem, value):
    ac = ActionChains(browser)
    ac.move_to_element(elem)
    time.sleep(0.2)
    ac.click()
    time.sleep(0.2)
    ac.send_keys(value)
    time.sleep(0.2)
    ac.send_keys(Keys.ENTER)
    time.sleep(0.2)
    ac.perform()
    time.sleep(0.1)

def delete_all_dohody(url):    
    browser = webdriver.Chrome(options= webdriver_options())
    time.sleep(1.0)
    browser.get(url)
   
    login(browser)

    input('Нажмите ENTER для удаления всех доходов за пределами рф...')
    out_d =  browser.find_element_by_id('react-tabs-3') #поиск вкладки "за пределами рф". все остальные элементы ищем внутри этой вкладки
    
    i = 0
    elems = out_d.find_elements_by_class_name('Spoiler_spoilerItemHeader__1RM7f') # поиск всех источников    
    print("осталось удалить:", len(elems))
    while True:
        if len(elems)<1:
            break      
        try:  
            buff = out_d.find_element_by_class_name('IncomeSources_buttons__2Vgg6') #поиск элемента с кнопкой удаления источника
            elem = buff.find_element_by_tag_name('button') # поиск кнопки
        except Exception:
            break

        ac = ActionChains(browser)
        ac.move_to_element(elem)
        time.sleep(0.2)
        ac.click()
        time.sleep(0.2)
        ac.perform()
        elem = None
        i += 1
        print("удалено: {} из {}".format(i, len(elems)))

    input('Удаление доходов завершено. Нажмите ENTER чтобы закрыть программу.')

def webdriver_options():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1024,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--start-maximized")
    return options

def check_debug(key_string):
    global DEBUG
    if DEBUG:
        input("Нажмите Enter чтобы " + key_string)
    else:
        print(key_string)

def get_kod_strany(isin):
    res = ""
    if len(isin) >= 12:
        k = isin[:2]
        if k.find("US") != -1:
            res = "840"
        elif k.find("IE") != -1:
            res = "372"
        elif k.find("JE") != -1:
            res = "832"
    return res

#на веб-странице присутствуют источники доходов и в пределах рф и за пределами рф.
#чтобы работать с элементами вкладки "за пределами рф" нужно выбирать соотв. элемент id= react-tabs-3, а уже в нем искать нужные поля и кнопки
def get_data(url, data):  
    browser = webdriver.Chrome(options= webdriver_options())
    time.sleep(1.0)
    browser.get(url)
    
    login(browser)
        
    input("Нажмите Enter чтобы начать заполнение...")
    items_worked = 0        
    for itm in data:
        items_worked += 1
        print("№ добавляемого дохода = ", items_worked)
        
        if DEBUG and items_worked >= 10:
            print(items_worked, " записей добавлено")
            break

        ## в боевом режиме раскомментировать    
        check_debug("добавить источник дохода.....")
        out_d =  browser.find_element_by_id('react-tabs-3')
        elem = out_d.find_element_by_class_name('form_buttons').click()
        time.sleep(0.1)

        # Spoiler_spoilerItemHeader__1RM7f
        check_debug("открыть последний источник дохода.....")
        out_d =  browser.find_element_by_id('react-tabs-3')
        elems = out_d.find_elements_by_class_name('Spoiler_spoilerItemHeader__1RM7f')    
        #print(elems)
        if len(elems)>0:
                ac = ActionChains(browser)
                ac.move_to_element(elems[-1])
                time.sleep(0.2)
                ac.click()
                time.sleep(0.2)
                ac.perform()
                time.sleep(0.1)

        #Наименование    
        check_debug("изменить наименование.....")        
        cnt_d = get_cnt_dohod_2(browser)
        print('cnt_d=', cnt_d)        
        if (cnt_d <= 0):
            print("нет ни одного источника дохода")
            sys.exit()
        # # cnt_d = 2        
        elem = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.NAME, 'Ndfl3Package.payload.sheetB.sources['+str(cnt_d - 1)+'].incomeSourceName')))
        elem.clear()
        elem.send_keys(itm.Emitent)
        time.sleep(0.1)
        
        #Страна. 840 -сша        
        check_debug("изменить страну источника выплаты.....")
        elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='Ndfl3Package.payload.sheetB.sources["+str(cnt_d - 1)+"].oksmIst']")))
        set_value_to_cmbbox(browser, elem, get_kod_strany(itm.Isin))    

        #Страна. 643 -россия
        check_debug("изменить страну зачисления выплаты.....") 
        elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='Ndfl3Package.payload.sheetB.sources["+str(cnt_d - 1)+"].oksmZach']")))
        set_value_to_cmbbox(browser, elem, "643")    

        #Код дохода  1010 - дивиденды   Ndfl3Package.payload.sheetB.sources[0].incomeTypeCode
        check_debug("изменить вид дохода.....")
        elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='Ndfl3Package.payload.sheetB.sources["+str(cnt_d - 1)+"].incomeTypeCode']")))
        set_value_to_cmbbox(browser, elem, '1010')    

        #Предоставить налоговый вычет   Не предоставлять вычет   Ndfl3Package.payload.sheetB.sources[0].taxDeductionCode
        check_debug("изменить предоставление вычета.....")
        elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='Ndfl3Package.payload.sheetB.sources["+str(cnt_d - 1)+"].taxDeductionCode']")))
        set_value_to_cmbbox(browser, elem, 'не')
        
        #Сумма дохода в валюте  (сумма операции + удержано ндфл эмитентом) Ndfl3Package.payload.sheetB.sources[1].incomeAmountCurrency 
        check_debug("изменить сумму дохода.....")
        elem = browser.find_element_by_id('Ndfl3Package.payload.sheetB.sources['+str(cnt_d - 1)+'].incomeAmountCurrency')    
        elem.clear()
        elem.send_keys(itm.Dohod)
        time.sleep(0.1)

        #Дата получения дохода  Ndfl3Package.payload.sheetB.sources[1].incomeDate
        check_debug("изменить дату получения дохода.....")        
        elem = browser.find_element_by_id('Ndfl3Package.payload.sheetB.sources['+str(cnt_d - 1)+'].incomeDate')    
        inpt = elem.find_element_by_tag_name("input")
        inpt.clear()
        if DEBUG:
            inpt.send_keys("31.12.2021" + Keys.ENTER)
        else:
            inpt.send_keys(itm.DateOperate + Keys.ENTER)

        time.sleep(0.1)
    
        #Дата уплаты налога ( равна дате получения)  Ndfl3Package.payload.sheetB.sources[1].taxPaymentDate
        check_debug("изменить дату уплаты дохода.....")
        elem = browser.find_element_by_id('Ndfl3Package.payload.sheetB.sources['+str(cnt_d - 1)+'].taxPaymentDate')    
        inpt = elem.find_element_by_tag_name("input")
        inpt.clear()
        inpt.send_keys(itm.DateOperate + Keys.ENTER)
        time.sleep(0.1)

        #Наименование валюты, 840 - доллар сша  Ndfl3Package.payload.sheetB.sources[0].currencyCode
        check_debug("изменить наименование валюты.....")
        elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='Ndfl3Package.payload.sheetB.sources["+str(cnt_d - 1)+"].currencyCode']")))
        set_value_to_cmbbox(browser, elem, '840')   

        #Определить курс автоматически  getCurrencyOnline    индексация checkbox_2 _3 _4 ....
        check_debug("включить автоматическое определение курса.....")
        out_d =  browser.find_element_by_id('react-tabs-3')
        out_d.find_element_by_xpath("//label[@for='checkbox_"+ str(cnt_d + 1) +"']").click()
        time.sleep(0.1)

        #Сумма налога с ин. гос-ве (в ин.валюте)  Ndfl3Package.payload.sheetB.sources[0].paymentAmountCurrency
        check_debug("изменить уплаченный налог в ин. гос-ве .....")
        elem = browser.find_element_by_id('Ndfl3Package.payload.sheetB.sources['+str(cnt_d - 1)+'].paymentAmountCurrency')    
        elem.clear()
        elem.send_keys(itm.Taxe)    
        time.sleep(0.1)

    input("Добавление доходов завершено, нажмите ENTER чтобы закрыть браузер.")

#код для добавления источников дохода из csv
data = get_data_from_csv('divs.csv')
#for i in data:
#    print(i.__dict__)

if len(data) > 0:
    get_data(link, data)

#код для удаления всех источников дохода за пределами рф
#delete_all_dohody(link)
