import requests
import requests
from requests import Session
from bs4 import BeautifulSoup
import re
import json

# Getting the cookies
cookie_url = "https://country-leaders.onrender.com/cookie"
req = requests.get(cookie_url)
cookies = req.cookies

# Saving the different urls in variables
root_url = "https://country-leaders.onrender.com/"
leaders_url = root_url + "leaders"
countries_url = root_url + "countries"

# Extracting the list of country codes and saving it in a variable
countries = requests.get(countries_url, cookies=cookies)
countries_list = countries.json()

# Getting the first paragraph about the leader
def get_first_paragraph(wikipedia_url, session: Session):
    """ 
    Function that will print the url and first paragraph of each leader's page
    :param wikipedia-url: the wikipedia url stored in the diictionary we create below
    :param session: session from requests to get faster  
    """
    print(wikipedia_url) 
    # We extract the HTML content from the url and store it in a variable
    wiki_content = session.get(wikipedia_url)
    html_content = BeautifulSoup(wiki_content.text, 'html.parser')
    # We find the h1 (there should be only one h1 but to make sure I added one class) and we take the first word that we store in a variable
    name = html_content.find("h1", class_="firstHeading").text[0]
    # Saving all the p from the page in a variable
    paragraphs = html_content.find_all('p')
    # Searching for the 1st p using the word contained in name
    for p in paragraphs:
        if p.get_text().__contains__(name):
            # But disgarding if it's a particular div (in FR pages, there are some p using the name before the correct paragraph)
            if not p.find_parent("div", class_="bandeau-cell"):                
                first_paragraph = p.get_text()
                # using some regex to clean the paragraphs : removing [number], [words], [all other combinations], Ecouter, ⓘ and content between // (phonetic info)
                first_paragraph = re.sub(r"\[\d+\]", "", first_paragraph)
                first_paragraph = re.sub(r"\[\w+\]", "", first_paragraph)
                first_paragraph = re.sub(r"\[.+\]", "", first_paragraph)
                first_paragraph = re.sub("Écouter", "", first_paragraph)
                first_paragraph = re.sub("ⓘ", "", first_paragraph)
                first_paragraph = re.sub(r"\/.+\/", "", first_paragraph)
                print(first_paragraph)
                break

# Getting the wikipedia urls
def get_leaders():
    '''
    Function that creates the correct urls for each country to get each leader's info and storing it in a variable
    and then that calls the get_first_paragraph function
    :return: the dictionnary with all the leaders' info
    '''
    with Session() as session:
        # Create the parameters for each country --> to add in the url and extract the info
        dict_leaders = {}
        for country in countries_list:
            params = { "country": country}
            # Try to get the info on each country page, we add the info from the page in our dictionary
            # We call the get_first_paragraph by using the wikipedia url that's now stored in our dictionary
            try:
                leaders = requests.get(leaders_url, cookies=cookies, params=params)
                dict_leaders[country]= leaders.json()
                for elem in dict_leaders[country]:
                    get_first_paragraph(elem["wikipedia_url"], session)
            # If it doesn't work, we get the cookies again and we do the same as in the try section
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

# We store the dictionary with all the leaders' info in a variable
leaders_per_country = get_leaders()


def save(json_filename):
    '''
    Function that saves our dictionary in a json file named "leaders.json
    :param json_filename: the variable storing the info we want to save in a json file
    '''
    with open("leaders.json", "w") as outfile: 
        json.dump(json_filename, outfile)

# Calling teh function to have our dictionary saved in a json file 
save(leaders_per_country)