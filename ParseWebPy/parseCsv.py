import csv
from os import read
from classes import DivInfo
from classes import IsinInfo

def get_isins_from_csv(namefile):
    input("Нажмите Enter чтобы загрузить ISINs из csv")
    cnt_row = 0
    isinInf = IsinInfo()
    try:
        with open(namefile, encoding='UTF-8', newline='') as f:
            reader = csv.reader(f, delimiter=';')    
            for row in reader:                
                cnt_row += 1
                #print(row)
                isinInf.add_isin(row)                
    except Exception as e:
        print("ошибка добавления isin в словарь")
        pass

    print("кол-во записей в файле = ", cnt_row)
    print("кол-во загруженных записей = ", len(isinInf.dict_isins))
    print()
    return isinInf.dict_isins


def get_data_from_csv(namefile):
    input("Нажмите Enter чтобы загрузить данные из csv")
    isins = get_isins_from_csv("ISINs.csv")
    data = []
    cnt_row = 0
    try:
        with open(namefile, encoding='UTF-8', newline='') as f:
            reader = csv.reader(f, delimiter=';')    
            for row in reader:
                divInf = DivInfo()
                cnt_row += 1
                #print(row)
                divInf.set_info(row)
                try:
                    divInf.Isin = isins[ divInf.Emitent]
                except Exception as e:
                    print(" не найден isin для ", divInf.Emitent)
                data.append(divInf)
                #data.append( [divInf.Namefile, divInf.NumOp, divInf.Emitent, divInf.Isin, divInf.Dohod, divInf.EmitentTaxe, divInf.DateOperate, divInf.Schet])
                #divInf.clear_infos()
    except Exception as e:
        print("ошибка парсинга csv-отчета ")
        pass

    # for i in data:
    #     print(i.__dict__)
    print("кол-во записей в файле = ", cnt_row)
    print("кол-во загруженных записей = ", len(data))
    print()

    return data
