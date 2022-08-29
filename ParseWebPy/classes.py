from decimal import Decimal
import decimal

class Indexes:
    def __init__(self) -> None:
        self.clear_indexes()

    def clear_indexes(self):
        self.BegTBL = -1
        self.endPG = -1
        self.begTypeDHD = -1
        self.endTypeDHD = -1
        self.iNumOp = -1
        self.iEmit = -1
        self.iISIN = -1
        self.iDHD = -1
        self.iTaxEmit = -1
        self.iDateOp = -1

class DivInfo:  
    def __init__(self) -> None:
        self.clear_infos()
    def clear_infos(self):
        self.DateOperate = ""
        self.Dohod = ""
        self.Polucheno = ""
        self.Emitent = ""
        self.Taxe = ""
        self.Komissia = ""
        self.Isin = ""
        
        self.Namefile = ""
        self.NumOp = ""       
        self.Schet = ""

    def set_info(self, row):
        if len(row) < 4: 
            return
        self.DateOperate = row[0][:10]        
        self.Emitent = row[2].strip()
        self.Taxe = row[3].strip().replace(",", ".") #уплоченый налог
        self.Komissia = row[4].strip().replace(",", ".") #комиссия банка
        self.Polucheno = row[1].strip().replace(",", ".") # полученный доход после вычета налога
        # self.Dohod = str(float(self.Polucheno) + float(self.Taxe))  #полный доход = уплоченный налог (10%) + полученный доход
        self.Dohod = str(round(float(self.Polucheno) + float(self.Taxe) + float(self.Komissia),2))  #полный доход = уплоченный налог (10%) + полученный доход + комиссия банка


class IsinInfo:
    def __init__(self) -> None:
        self.dict_isins = {}
        pass
    
    def add_isin(self, row):
        if len(row) <2:
            return
        self.dict_isins[row[0].strip()] = row[1].strip()
    