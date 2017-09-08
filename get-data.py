import time
import sys
import json
import datetime
import shutil
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    path = "./geckodriver.exe"
    driver = webdriver.Firefox('.')
    return driver

def read_game_data():
    try:
        with open('games-data.json', 'rb') as f:
            gameData = json.load(f)
    except:
        gameData = {}
    return gameData

def read_games():
    with open('games.json', 'rb') as f:
        return  json.load(f)

def get_all_data(driver, games, gameData):
    for i, (_id, game) in enumerate(games.iteritems()):
        sys.stdout.write("Getting Game %d of %d           \r" % (i+1, len(games)))
        sys.stdout.flush()
        if _id in gameData.keys():
            continue
        driver.get(game['link'])
        game_data = get_game_data(driver, i+1, len(games))
        gameData[_id] = game
        gameData[_id]['data'] = game_data
        write_game_data(gameData)

def get_game_data(driver, gameNumber, totalNumber):
    game_data = {}
    # go to the matchs tatistics page
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.primary-content a')))
    try:
        matchStats = driver.find_element_by_xpath("//*[text()[contains(., 'Match Statistics...')]]").click()
    except:
        pass
    # get the innings available
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, 'btnGo2')))
    innings = driver.find_elements_by_css_selector("#drpInnings option")
    inningsText = [x.text for x in innings]
    # if innings occured
    if len(inningsText) != 0:
        # for each innings, select the values and get the data
        for i, inning in enumerate(inningsText[1:]):
            ball = []
            bowler = []
            batter = []
            score = []
            result = []
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#drpInnings option')))
            options = driver.find_elements_by_css_selector("#drpInnings option")
            for option in options:
                if inning == option.text:
                    option.click()
                    if i == 0:
                        displayOptions = driver.find_elements_by_css_selector('#drpFunction option')
                        for display in displayOptions:
                            if 'Ball by Ball' in display.text:
                                display.click()
                    # displayOptions = driver.find_elements_by_css_selector("#drpFunction option")[1].click()
                    driver.find_element_by_id("btnGo2").click()
                    table = driver.find_elements_by_css_selector(".RVDataGridItem")
                    if len(table) > 0:
                        for j, t in enumerate(table):
                            sys.stdout.write("%.2f%% Data Gathered for Innings %d... Game %d of %d                            \r" % (float(j) * 100 / len(table), i+1, gameNumber, totalNumber))
                            sys.stdout.flush()
                            try:
                                ball.append(t.text.split(" ")[0].encode('ascii', 'ignore'))
                                bowler.append(' '.join(t.text.split(" ")[1:]).split(" to ")[0].encode('ascii', 'ignore'))
                                batter.append(' '.join(t.text.split(" ")[1:]).split(" to ")[1].split(":")[0].encode('ascii', 'ignore'))
                                score.append(t.text.split(" ")[-1].encode('ascii', 'ignore'))
                                result.append(' '.join(t.text.split(" ")[:-1]).split(": ")[1].encode('ascii', 'ignore'))
                            except:
                                break
                        sys.stdout.write("100%% data Gathered for Innings %d... Game %d of %d                                 \r" % (i, gameNumber, totalNumber))
                        game_data[inning] = {}
                        game_data[inning]['ball'] = ball
                        game_data[inning]['bowler'] = bowler
                        game_data[inning]['batter'] = batter
                        game_data[inning]['score'] = score
                        game_data[inning]['result'] = result
                    break
    return game_data

def write_game_data(gameData):
    with open("games-data.json", 'wb') as f:
        json.dump(gameData, f, indent=2)
    shutil.copy('games-data.json', 'games-data-backup.json')

def main():
    # sys.path.append("C://Desktop/")
    driver = init_driver()
    games = read_games()
    gameData = read_game_data()
    get_all_data(driver, games, gameData)

if __name__ == "__main__":
    main()
