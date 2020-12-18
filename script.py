import urllib.request
import datetime
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
LAST_UPDATE = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')


def get_patient_details():
    URL = "https://www.pref.kagawa.lg.jp/yakumukansen/kansensyoujouhou/kansen/se9si9200517102553.html"
    with urllib.request.urlopen(URL) as response:
        html = response.read().decode("utf-8")
        sp = BeautifulSoup(html, "html.parser")
        re_date_of_confirmation = re.compile(r"^(\d*)月(\d*)日（[日月火水木金土]曜日）")
        re_gender = re.compile(r"^([男女])")
        re_generation = re.compile(r"^\d*[歳代]")
        re_address = re.compile(r"^(.*[市町村都道府県].*)")
        pt_ls_d = datetime.datetime(2020, 3, 17)
        template = {
            "date": LAST_UPDATE,
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
        with open("patients.json", "w", encoding="utf-8") as f:
            json.dump(template, f, indent=4, ensure_ascii=False)


def readCSV(f):
    result = []
    for i, line in enumerate(f.split("\n")):
        if i != 0:
            result.append(line.strip().split(","))
    return result


def generateInspectionsArray():
    csv_files = [
        "https://opendata.pref.kagawa.lg.jp/dataset/359/resource/4390/%E6%A4%9C%E6%9F%BB%E4%BB%B6%E6%95%B0%EF%BC%88%E4%BB%A4%E5%92%8C2%E5%B9%B411%E6%9C%8830%E6%97%A5%E3%81%BE%E3%81%A7%EF%BC%89.csv",
        "https://opendata.pref.kagawa.lg.jp/dataset/359/resource/4946/%E6%A4%9C%E6%9F%BB%E4%BB%B6%E6%95%B0%EF%BC%88%E4%BB%A4%E5%92%8C2%E5%B9%B412%E6%9C%881%E6%97%A5%E3%81%8B%E3%82%89%EF%BC%89.csv",
    ]
    inspections_number = []
    labels = []
    for i, url in enumerate(csv_files):
        with urllib.request.urlopen(url) as response:
            if i == 0:
                f = response.read().decode("shift-jis")
                for csv_arr in readCSV(f):
                    if len(csv_arr) == 9:
                        a_day_inspections_number = int(csv_arr[1]) + int(csv_arr[2]) + int(csv_arr[5]) + int(csv_arr[6])
                        labels.append(csv_arr[0])
                        inspections_number.append(a_day_inspections_number)
            elif i == 1:
                f = response.read().decode("shift-jis")
                for csv_arr in readCSV(f):
                    if csv_arr != [""]:
                        a_day_inspections_number = int(csv_arr[1]) + int(csv_arr[3])
                        labels.append(csv_arr[0])
                        inspections_number.append(a_day_inspections_number)
    return {"inspections_count": inspections_number, "lables": labels}

summary_inspections_dic = generateInspectionsArray()

def generateSummary():
    URL = "https://www.pref.kagawa.lg.jp/kocho/koho/kohosonota/topics/wt5q49200131182439.html"
    results = {}
    with urllib.request.urlopen(URL) as response:
        html = response.read().decode("utf-8")
        sp = BeautifulSoup(html, "html.parser")
        if len(sp.select("[summary=\"香川県の発生状況一覧\"] tbody tr")[-1].select("td")) == 6:
            for i, td in enumerate(sp.select("[summary=\"香川県の発生状況一覧\"] tbody tr")[-1].select("td")):
                txt = td.get_text(strip=True).replace("人", "")
                if i == 0:
                    results["陽性患者数"] = int(txt)
                elif i == 1:
                    results["うち直近1週間"] = int(txt)
                elif i == 2:
                    results["現在感染者数"] = int(txt)
                elif i == 3:
                    results["死亡"] = int(txt)
                elif i == 4:
                    results["退院・退所"] = int(txt)
                elif re.match(r"^＞＞（\d）(.*)", txt):
                    results["対策期のレベル"] = re.match(r"^＞＞（\d）(.*)", txt).group(1)
        else:
            print("県のサイトの更新がありました。")
    main_summary_template = {
        "date": LAST_UPDATE,
        "attr": "検査実施件数",
        "value": sum(summary_inspections_dic["inspections_count"]),
        "children": [
            {
                "attr": "陽性患者数",
                "value": results["陽性患者数"],
                "children": [
                    {
                        "attr": "入院中",
                        "value": results["現在感染者数"]
                    },
                    {
                        "attr": "退院",
                        "value": results["退院・退所"]
                    },
                    {
                        "attr": "死亡",
                        "value": results["死亡"]
                    },
                    {
                        "attr": "調査中",
                        "value": 0
                    }
                ]
            }
        ]
    }
    with open("main_summary.json", "w", encoding="utf-8") as f:
            json.dump(main_summary_template, f, indent=4, ensure_ascii=False)


def main():
    get_patient_details()
    generateSummary()
    generateInspectionsArray()


if __name__ == "__main__":
    main()
