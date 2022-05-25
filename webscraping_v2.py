from bs4 import BeautifulSoup
import requests
from csv import writer



url = "https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Optional.html" ##(URL for desired API)
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

with open ('Optional.csv', 'w', encoding = 'utf8', newline = '') as f:
    thewriter = writer(f)
    header = ["ID","Method Modifier and Type", "Method Name", "Method Description"]
    thewriter.writerow(header)
    member_summary = soup.find_all("table", class_ = "memberSummary")
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

