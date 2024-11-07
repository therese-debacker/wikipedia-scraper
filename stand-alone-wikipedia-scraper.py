import requests
import requests
from requests import Session
from bs4 import BeautifulSoup
import re
import json

cookie_url = "https://country-leaders.onrender.com/cookie"
req = requests.get(cookie_url)
cookies = req.cookies

countries_url = "https://country-leaders.onrender.com/countries"
root_url = "https://country-leaders.onrender.com/"
leaders_url = root_url + "leaders"

countries = requests.get(countries_url, cookies=cookies)
countries_list = countries.json()


def get_first_paragraph(wikipedia_url, session: Session):
    print(wikipedia_url) 
    wiki_content = session.get(wikipedia_url)
    html_content = BeautifulSoup(wiki_content.text, 'html.parser')
    name = html_content.find("h1").text[0]
    paragraphs = html_content.find_all('p')
    for p in paragraphs:
        if p.get_text().__contains__(name):
            first_paragraph = p.get_text()
            first_paragraph = re.sub(r"\[\d+\]", "", first_paragraph)
            first_paragraph = re.sub(r"\[\w+\]", "", first_paragraph)
            first_paragraph = re.sub(r"\[.+\]", "", first_paragraph)
            print(first_paragraph)
            break

def get_leaders():
    with Session() as session:
        dict_leaders = {}
        for country in countries_list:
            params = { "country": country}
            try:
                leaders = requests.get(leaders_url, cookies=cookies, params=params)
                dict_leaders[country]= leaders.json()
                for elem in dict_leaders[country]:
                    get_first_paragraph(elem["wikipedia_url"], session)
            except:
                cookie_url = "https://country-leaders.onrender.com/cookie"
                # Query the enpoint, set the cookies variable and display it (2 lines)
                req = requests.get(cookie_url)
                cookies = req.cookies
                leaders = requests.get(leaders_url, cookies=cookies, params=params)
                dict_leaders[country]= leaders.json()
                for elem in dict_leaders[country]:
                    get_first_paragraph(elem["wikipedia_url"], session)
    return dict_leaders

leaders_per_country = get_leaders()


# #leaders_per_country = get_leaders() --> return le dict et utiliser variable pour json

def save(json_filename):
    with open("leaders.json", "w") as outfile: 
        json.dump(json_filename, outfile)

save(leaders_per_country)