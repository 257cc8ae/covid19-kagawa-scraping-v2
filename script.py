import urllib.request
import datetime
from bs4 import BeautifulSoup
import re

def get_patient_details():
    URL = "https://www.pref.kagawa.lg.jp/yakumukansen/kansensyoujouhou/kansen/se9si9200517102553.html"
    with urllib.request.urlopen(URL) as response:
        html = response.read().decode("utf-8")
        sp = BeautifulSoup(html, "html.parser")
        last_update = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        print(last_update)
        re_date_of_confirmation = re.compile(r"^\d*月\d*日（[日月火水木金土]曜日）")
        re_case = re.compile(r"^\d*")
        re_gender = re.compile(r"^[男女]")
        re_generation = re.compile(r"^\d*[歳代]")
        re_address = re.compile(r"^.*[市町]")

        for tag in sp.select(".datatable tbody tr"):
            tr_summary = BeautifulSoup(tag,"html.parser")
            for tds in tr_summary.select("td"):
                pass

def main():
    get_patient_details()

if __name__ == "__main__":
    main()