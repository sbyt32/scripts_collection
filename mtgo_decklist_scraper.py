#   MTGO Results Scraper
# * Grab data from https://www.mtgo.com/en/mtgo/decklists
# * Stores data as a .json file in decklists/*.json
# * Organized by Year -> Month -> Event Name
# * Limitations:
    # ! Site redirects to the most recent page (currently Dec 2022) if the page is invalid (like searching for January 2026).
    # ! Script checks whether or not the the file exists after parsing the data, inefficency.
# * Notes:
    # * 2018 is used as the starting year because that was when more "Constructed" league data was being shared.
    # *
    #
    # * You could use <select id="decklistMonth"> to see which months are fetchable, in the future.
        # Same with <select id="decklistYear">
        # This would fix the limitation issue, at the cost of just one more request to the site.
    # Not sure what "Card_Code" corresponds to in the .json files
# * Libraries:
import bs4
import requests
import json
import re
import os

# * Change below to True to fetch 2016 & 2017
get_pre_2018 = False

years_to_fetch = []

def request_wrapper(link:str):
    try:
        req = requests.get(link)
    except requests.exceptions.Timeout:
        print(f"Request to {link} timed out! Attempting again.")
        req = requests.get(link)
    if not req.ok:
        raise SystemExit(f"Request failed! Status: {req.status_code}")
    return req


if get_pre_2018:
    years_to_fetch += ["2017", "2018"]

years_to_fetch += ['2018','2019', '2020', '2021', '2022']

for years in years_to_fetch:
    for months in range(1,13):

        mtgo_lists = request_wrapper(f"https://www.mtgo.com/en/mtgo/decklists/{years}/{months:02}")
        for mtgo_event_link in bs4.BeautifulSoup(mtgo_lists.text, 'html.parser').select("li.decklists-item"):
            mtgo_event_page = mtgo_event_link.find('a', href=True)

            single_event_page = request_wrapper(f"https://www.mtgo.com{mtgo_event_page['href']}")
            grabbed_decklists = bs4.BeautifulSoup(single_event_page.text, 'html.parser')
            pattern = re.compile(r'window.MTGO.decklists.data = {(.*?)};', re.DOTALL) #  * The decklist data is held like this in the .html page. 
            find_script = grabbed_decklists.find("script", text=pattern)

            if find_script:
                grab_event_data = pattern.search(find_script.text)

                if grab_event_data:
                    data = grab_event_data.group()
                    data_as_json:object = json.loads(data[28:-1]) # * Exclude the first 28 for the 'window.MTGO.decklists.data = ' part and exclude the last character for the ;

                    filename = f'decklists/{years}/{months}/{data_as_json["_id"]}.json'

                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as decklist:
                        decklist.write(json.dumps(data_as_json, indent=2))
