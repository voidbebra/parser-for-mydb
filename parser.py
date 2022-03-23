from datetime import datetime
import re
from time import sleep
import pymysql
import requests
import fake_useragent
from config_for_db import host, user, password, db_name
from bs4 import BeautifulSoup as BS


def open_connect():
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("connection opened")
    except Exception as ex:
        print(ex)
    return connection

def main():
    connection=open_connect()
    try:
        session = requests.Session()

        urlpost="https://schedule.puet.edu.ua/ajax.php"

        user = fake_useragent.UserAgent().random
        header={
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'schedule.puet.edu.ua',
            'Origin': 'https://schedule.puet.edu.ua',
            'Referer': 'https://schedule.puet.edu.ua/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': user
        }
        datas0 = {
            "date_s": f"{datetime.now().strftime('%d.%m.%Y')}",
            "date_e": "22.03.2022",
            "course": "1",
            "num": "1",
            "spec_id": "543",
            "forma": "1",
            "owner": "44",
            "call": "get_schedule"
        }
        datas1 = {
            "date_s": f"{datetime.now().strftime('%d.%m.%Y')}",
            "date_e": "05.06.2022",
            "course": "1",
            "num": "2",
            "spec_id": "949",
            "forma": "1",
            "owner": "44",
            "call": "get_schedule"
        }
        datas2 = {
            "date_s": f"{datetime.now().strftime('%d.%m.%Y')}",
            "date_e": "05.06.2022",
            "course": "1",
            "num": "10",
            "spec_id": "949",
            "forma": "1",
            "owner": "44",
            "call": "get_schedule"
        }
        datas3 = {
            "date_s": f"{datetime.now().strftime('%d.%m.%Y')}",
            "date_e": "05.06.2022",
            "course": "1",
            "num": "4",
            "spec_id": "949",
            "forma": "1",
            "owner": "44",
            "call": "get_schedule"
        }

        with connection.cursor() as cursor:   
            cursor.execute("TRUNCATE TABLE `lessons2`;")
            for iteration in range(1):
                insertq=""
                try:
                    datespisok=[]
                    cursor.execute("SELECT date FROM `lessons2`;")
                    rows = cursor.fetchall()
                    for row in rows:
                        datespisok.append(row["date"])
                    #print(datespisok)
                except Exception as e:
                    print(e)
                if iteration == 0:
                    resp=session.post(urlpost, data=datas0, headers=header)
                elif iteration == 1:
                    resp=session.post(urlpost, data=datas1, headers=header)
                elif iteration == 2:
                    resp=session.post(urlpost, data=datas2, headers=header)
                elif iteration == 3:
                    resp=session.post(urlpost, data=datas3, headers=header)
                page = BS(resp.content, 'html.parser')
                td_all=page.find_all('td')
                
                date=f"{datetime.now().strftime('%d.%m')}"
                x=1
                for td in td_all:
                    if td.get('colspan') == '10':
                        print(f"дата: {td}")
                        x=1
                    else:
                        if td.text == ' ':
                            print(f"--{x}: empty")
                        else:
                        #for item in td:
                            #group=td.find
                            print(f"--{x}:")
                            for item in td:
                                if item!="<br/>":
                                    print("\t\t",item)
                            
                        x=x+1
                    # проверка на дату
                    if td.get('colspan') != '10':
                        # проверка на пустой элемент 
                        if td.text != ' ':
                            cursor.execute(f"SELECT * FROM `lessons2` WHERE date = '{date}';")
                            row=cursor.fetchall()[0]
                            if row[f'les{x}'] != '-':
                                insertq=f"UPDATE `lessons2` SET les{x} = '{row[f'les{x}']}\n{tospisok(td)}' WHERE date = '{date}';"
                            else:
                                insertq=f"UPDATE `lessons2` SET les{x} = '{tospisok(td)}' WHERE date = '{date}';"
                            cursor.execute(insertq)
                            #print(insertq)    
                        x=x+1
                    else:
                        date=td.text.split(', ')[1][:5]
                        if date_already_exists(date, datespisok):
                            insertq=f"INSERT INTO `lessons2` (date) VALUES ('{date}');"
                            cursor.execute(insertq)
                        x=1
                print(f"{iteration+1} iteration done")
            connection.commit()
            print("table updated")
            connection.close()
            print("connection close")
    except Exception as e:
            print("error: ", e)


def tospisok(lst):
  sheesh = []
  # преобразование бс4.элемент.тег в список
  for i in lst:
    sheesh.append(str(i))
  # слепить все элементы списка в строку
  string="".join(sheesh)
  # преобразовать обратно в список игнорируя теги
  newstring= (re.split("<td>|</td>|<small>|</small>|<br>|<br/>|</br>|<hr/>|<strong>|</strong>", string))
  new =[]
  # удаление пустых элементов /в принципе необязательно 
  for i in range(len(newstring)):
      if newstring[i] != '':
          new.append(newstring[i])
  # это вообще мем но пусть будет
  if len(new) == 6:
    a=new[0],new[1],new[4]
    return ' '.join(a)
  elif len(new) == 7:
    a=new[4],new[0],new[1],new[5]
    return ' '.join(a)
  elif len(new) == 14:
    a=new[4],new[0],new[1],new[5],"\n",new[11],new[7],new[8],new[12]
    return ' '.join(a)
  else:
    return 0

def date_already_exists(date, spisok):
    for el in spisok:
        if el == date: return False
    return True

def waiting():#запускать каждый сутки в час ночи
    while True:
        time= datetime.now().time().strftime("%H")
        print(time, "H")
        if time == "01":
            print("start of update...")
            main() 
        sleep(60*55)
            
if __name__ == "__main__" :
    waiting()
    