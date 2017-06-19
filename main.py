from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import json

def init_driver():
    driver = webdriver.PhantomJS()
    return driver

def get_all_data(driver):
    games = read_games()
    idx = 0
    with open('info.json', 'rb') as f:
        info = json.load(f)
    for j, (entity, data) in enumerate(info['entities'].iteritems()):
        sys.stdout.write("Getting " + entity + "(" + str(j+1) + ' of ' + str(len(info['entities'])) + ")\n")
        for year in info['Years']:
            print 'Getting ' + year + "..."
            driver = get_games_page(driver, data['id'], year, data['competition'])
            games, _ = get_games_data(driver, games, entity, year)
            write_data(games)
    return games, idx

def read_games():
    try:
        with open("games.json", 'rb') as f:
            return json.load(f)
    except:
        return {} 

def write_data(games):
    with open("games.json", 'wb') as f:
        json.dump(games, f, indent=2)

def get_games_page(driver, eid, yr, comp):
    driver.get('http://mycricket.cricket.com.au/common/pages/public/rv/draw.aspx?entityid=' + str(eid) + '&id=RVFIXTURE')
    year_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, 'ctl00$SelectorBarPlaceHolder$rvsb$rvsbc_0$lc')))
    el = driver.find_element_by_name('ctl00$SelectorBarPlaceHolder$rvsb$rvsbc_0$lc')
    for option in el.find_elements_by_tag_name('option'):
        if option.text == yr:
            option.click()
            break
    year_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, 'ctl00$SelectorBarPlaceHolder$rvsb$rvsbc_3$lc')))
    el = driver.find_element_by_name('ctl00$SelectorBarPlaceHolder$rvsb$rvsbc_3$lc')
    for el_option in el.find_elements_by_tag_name('option'):
        if el_option.text == comp:
            el_option.click()
            break
    driver.find_element_by_name("ctl00$SelectorBarPlaceHolder$rvsb$ctl08").click()
    return driver 

def get_games_data(driver, games, entity, year):
    rows = driver.find_elements_by_css_selector("tr")
    for j, row in enumerate(rows):
        sys.stdout.write("%.2f%% Completed    \r" % (float(j) * 100 / len(rows)))
        sys.stdout.flush()
        if row.get_attribute("class") == 'fixtureRow':
            game_data = []
            els = row.find_elements_by_tag_name("td")
            datapoints = ['date', 'home', 'result', 'away', 'ground']
            for el in els:
                try:
                    link = el.find_element_by_tag_name('a')
                except:
                    continue 
                if 'http://' not in link.get_attribute('href'):
                    continue
                gameid = link.get_attribute("href").split('matchID=')[1].split("%20")[0]
                if gameid in games.keys():
                    gameid = None
                    break
                games[gameid] = {}
                games[gameid]['entity'] = entity
                games[gameid]['link'] = link.get_attribute('href')
            if gameid is not None:
                games[gameid]
                for tag, el in zip(datapoints, els[:len(datapoints)]):
                    elementText = el.text
                    if tag == 'date' and len(elementText.split(",")) > 1:
                        del games[gameid]
                        break
                    games[gameid][tag] = elementText
    return games, driver

def main():
    start_time = datetime.datetime.now()
    ## init driver 
    driver = init_driver()
    ## get the page showing the list of all games
    games, idx  = get_all_data(driver)
    # write to file 
    write_data(games)
    end_time = datetime.datetime.now()

if __name__ == "__main__":
    main()