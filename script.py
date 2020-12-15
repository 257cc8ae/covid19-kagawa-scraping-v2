import urllib.request
import datetime
from bs4 import BeautifulSoup
import re
import json


def get_patient_details():
    URL = "https://www.pref.kagawa.lg.jp/yakumukansen/kansensyoujouhou/kansen/se9si9200517102553.html"
    with urllib.request.urlopen(URL) as response:
        html = response.read().decode("utf-8")
        sp = BeautifulSoup(html, "html.parser")
        last_update = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        re_date_of_confirmation = re.compile(r"^(\d*)月(\d*)日（[日月火水木金土]曜日）")
        re_gender = re.compile(r"^([男女])")
        re_generation = re.compile(r"^\d*[歳代]")
        re_address = re.compile(r"^(.*[市町村都道府県].*)")
        pt_ls_d = datetime.datetime(2020, 3, 17)
        template = {
            "date": last_update,
            "data": []
        }
        for i, tag in enumerate(sp.select(".datatable tbody tr")):
            if i == 0:
                pass
            else:
                patient_data = {
                    "リリース日": "",
                    "居住地": "",
                    "年代": "",
                    "性別": "",
                    "date": "",
                }
                for i, td in enumerate(tag.select("td")):
                    txt = td.get_text(strip=True)
                    if i == 1 and re_date_of_confirmation.match(txt) == None:
                        patient_data["年代"] = txt
                        patient_data["リリース日"]: str = str(pt_ls_d)
                        patient_data["date"]: str = str(pt_ls_d.date())
                    elif re_date_of_confirmation.match(txt):
                        rp = re_date_of_confirmation.match(txt)
                        dt = datetime.datetime(
                            2020, int(rp.group(1)), int(rp.group(2)))
                        pt_ls_d = dt
                        patient_data["リリース日"]: str = str(dt)
                        patient_data["date"]: str = str(dt.date())
                    elif re_address.match(txt):
                        patient_data["居住地"] = txt
                    elif re_gender.match(txt):
                        patient_data["性別"] = txt + "性"
                    elif re_generation.match(txt):
                        patient_data["年代"] = txt
                template["data"].append(patient_data)
        with open("patients.json","w",encoding="utf-8") as f:
            json.dump(template, f, indent=4, ensure_ascii=False)

def main():
    get_patient_details()


if __name__ == "__main__":
    main()
