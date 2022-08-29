
# -*- coding: utf-8 -*-
import os
import sys
import fitz
import csv
from classes import DivInfo
from classes import Indexes

print()
print()


FOLDERREP = "./reports"
pdfs = []
for item in os.listdir(FOLDERREP):
    if item.find(".pdf") != -1:
        pdfs.append(item)   

idxs = Indexes()
divInf = DivInfo()
data = []
#PyMuPDF
cnt_wrk = 0
cnt_pdfs = len(pdfs)
s4et = "" #INSERT BANK ACCOUNT 20 characters


def parse_stroka( stroka):
    schet = False
    dateOp = False
    taxe = False
    dhd = False
    isin = False
    nameEm = False
    numOp = False
    divInf.Namefile = stroka[0]

    # проход по строке с конца в начало. 
    # На 20-21 годы формат строки : Тип дохода, номер операции, Эмитент, Сумма операции, Удержано НДФЛ эмитентом, Удержано НДФЛ банком, Дата опер., Счет зачисл.
    # Налог банком не удерживается.
    for itm in range(len(stroka) - 1, -1, -1):
        if stroka[itm].find(s4et) != -1: # если нашли вал. счет
            num = stroka[itm].find(s4et)
            try:
                int(stroka[itm][num:num+20])   #если удается вал. счет преобразовать в число, значит это точно счет :)
                divInf.Schet = stroka[itm][num:num+20]
                schet = True

                divInf.DateOperate = stroka[itm][0:10].strip() #из этой же строки берем дату. (из pdf дата парсится в одной строке со счетом)
                dateOp = True                
            except ValueError as e:
                divInf.Schet = "ошибка"
                divInf.DateOperate = "ошибка"
                pass
            continue

        #если счет найден, а доход еще нет, то обрабатываем налог и доход. Налог может быть равен 0 или вовсе отсутствовать 
        if dateOp and schet and not(dhd): 
            try:
                divInf.EmitentTaxe = 0.0
                divInf.Dohod = 0.0
                float(stroka[itm]) #пытаемся конвертировать текущ. и след. элементы (налог и доход соотв-но)
                float(stroka[itm - 1])
                divInf.EmitentTaxe = float(stroka[itm]) #если успешно конвертнули, то записываем
                divInf.Dohod = float(stroka[itm - 1])
            except ValueError as e: #если ошибка конвертации, то предполагаем, что налог отсутсвует, а текущий элемент это доход
                divInf.EmitentTaxe = 0.0
                divInf.Dohod = stroka[itm]
            finally:
                taxe = True
                dhd = True
            continue
        
        # если найден доход, а ISIN - нет, то ищем ISIN
        # формат строки "ISIN: XXXXXXXXXXXX". Само число может быть на другой строке
        if dhd and stroka[itm].find("ISIN:") != -1:
            if len(stroka[itm]) > 12:  #если ключевое слово ISIN нашли и размер строки больше 12, то в строке находится само число ISIN
                divInf.Isin = stroka[itm][-12:].strip() #вытаскиваем число
            else: #если строка < 12, то число ISIN находится в предыдущем элементе
                divInf.Isin = stroka[itm + 1] 
            isin = True
            continue
        
        # если нашли isin, но не нашли наименование эмитента, то ищем его
        # наименование может состоять из нескольких частей в разных строках. Первая часть наименования может быть в одной строке с номером операции.
        # Пример "25987308 Exxon Mobil" "Corporation" "ISIN:" "US30231G1022"
        if isin and not(nameEm):
            divInf.Emitent = stroka[itm] + divInf.Emitent #собираем все строки с частями наименования в одну
            try:
                int(stroka[itm][:8]) #предполагаем, что вначале строки лежит номер операции. пытаемся конвертнуть в число
                divInf.NumOp = stroka[itm][:8] #если успешно, то записываем его ..
                numOp = True
                divInf.Emitent = divInf.Emitent[8:] # .. и из собранной строки вырезаем номер операции
                nameEm = True
            except ValueError as e:
                continue

    return ""

#вторая версия. работает лучше первой. 
# 1. ищем вал. счет; 2. от него двигаясь назад собираем строку; 3. парсим ее; 4.записываем в массив данных; 
# 5. переход к 1 шагу, пока не пройдем весь pdf; 6. собранный массив данных сохраняем в csv
for item in pdfs:
    doc = fitz.Document(FOLDERREP+ "/"+item)    
    print("{} из {}".format( cnt_wrk , cnt_pdfs))
    cnt_wrk += 1

    for page in doc:
        pg = page.get_text()
        pg_txt = pg.split('\n')        
        idxs.endPG = len(pg_txt)     

        #поиск начала таблицы по ключевому слову
        for idx in range(idxs.endPG):        
            if pg_txt[idx].find("валюта – USD") != -1 :
                idxs.BegTBL = idx
                break
        
        if idxs.BegTBL == -1:
            break

        #поиск строк в таблице
        stroka = []
        for idx in range(idxs.BegTBL, idxs.endPG):
            stroka.clear()            
            if pg_txt[idx].find(s4et) != -1 :  #если нашли валютный счет
                stroka.append(item)
                for itm in range(idx, idxs.BegTBL, -1):
                    stroka.insert(1, pg_txt[itm])
                    if pg_txt[itm].find("Дивиденды по ценным ") != -1:
                        break
                #print("stroka=", stroka)
                parse_stroka(stroka)
                data.append( [divInf.Namefile, divInf.NumOp, divInf.Emitent, divInf.Isin, divInf.Dohod, divInf.EmitentTaxe, divInf.DateOperate, divInf.Schet])
                divInf.clear_infos()
print(*data, sep='\n')   
with open('divs.csv', 'w', encoding='UTF-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

cnt_schet = 0
#поиск всех перечислений на валютный счет 
for item in pdfs:
    doc = fitz.Document(FOLDERREP+ "/"+item)        
    for page in doc:
        pg = page.get_text()
        pg_txt = pg.split('\n')
        endPG = len(pg_txt)
        for idx in range(endPG): 
            if pg_txt[idx].find(s4et) != -1 :
                cnt_schet += 1
                print("{} | {} | {} | {} | {}".format( item, pg_txt[idx-3], pg_txt[idx-2], pg_txt[idx-1], pg_txt[idx]))
print("кол-во найденых перечислений на счет = ", cnt_schet)
print("кол-во собранных данных = ", len(data))

print('Обработка завершена')
