from bs4 import BeautifulSoup

with open('Optional.html', 'r') as html_file:
    content = html_file.read()

    soup = BeautifulSoup(content, "lxml")
    member_summary = soup.find_all("table", class_ = "memberSummary")
    methods = member_summary[-1]
    methods = methods.find_all("tr", id=lambda value: value and value.startswith("i"))
    for method in methods:
        #print(method)
        #print(method.find("div", class_ = "block"))
        method_modifier = method.find("td", class_ = "colFirst").text
        method_name = method.find("td", class_ = "colLast").code.text
        method_description = method.find("div", class_ = "block").text
        print("Method Modifier and Type:" + method_modifier + "\n" + "Method Name:" + method_name + "\n" + "Method Description:" + method_description + "\n")

    
    
