from bs4 import BeautifulSoup
import requests
from csv import writer

my_file = open("java.util urls.txt", "r") #CHANGE THE URL TEXT FILE TO THE PACKAGE YOU WANT TO EXTRACT
url = my_file.readlines()
print(url)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
for i in url:
    i = i.replace("\n", "")
    class_name = i.replace("https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/" , "")
    class_name = class_name.replace(".html\n", "")
    page = requests.get(i, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(class_name + ".csv")
    
    with open (class_name + '.csv', 'w', encoding = 'utf8', newline = '') as f:
        thewriter = writer(f)
        header = ["ID","Method Modifier and Type", "Method Name", "Method Description"]
        thewriter.writerow(header)
        member_summary = soup.find_all("table", class_ = "memberSummary")
        if len(member_summary) == 0:
            continue
        methods = member_summary[-1]
        n = 0
        methods = methods.find_all("tr", id=lambda value: value and value.startswith("i"))
        for method in methods:
            ids = "i" + str(n)  ##desired identity name
    
            method_modifier = method.find("td", class_ = "colFirst").text
            method_name = method.find("span", class_ = "memberNameLink").text
            method_description = method.find("div", class_ = "block").text
            print("Method Modifier and Type:" + method_modifier + "\n" + "Method Name:" + method_name + "\n" + "Method Description:" + method_description + "\n")
            info = [ ids ,method_modifier, method_name,method_description]
            n += 1
            thewriter.writerow(info)
