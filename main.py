from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from deep_translator import GoogleTranslator
import time
import os
from dotenv import load_dotenv
import sentimentAnalysis
import pandas as pd
import requests

load_dotenv()

username = os.getenv("X_USER")
password = os.getenv("X_PASSWORD")

gm_models = [
    # 2024
    "Fiat Strada",
    "Volkswagen Polo",
    "Chevrolet Onix",
    "Hyundai HB20",
    "Fiat Argo"
    """Volkswagen T-Cross",
    "Chevrolet Tracker",
    "Hyundai Creta",
    "Fiat Mobi",
    "Nissan Kicks",
    # 2023
    "Fiat Strada",
    "Volkswagen Polo",
    "Chevrolet Onix",
    "Hyundai HB20",
    "Chevrolet Onix Plus",
    "Fiat Mobi",
    "Volkswagen T-Cross",
    "Fiat Argo",
    "Chevrolet Tracker",
    "Hyundai Creta",
    # 2022
    "Fiat Strada",
    "Hyundai HB20",
    "Chevrolet Onix",
    "Chevrolet Onix Plus",
    "Fiat Mobi",
    "Volkswagen Gol",
    "Chevrolet Tracker",
    "Volkswagen T-Cross",
    "Fiat Argo",
    "Jeep Compass","""
]
QUERYS = ["pintura", "acabamento"]
FILTER = "&src=typed_query&f=live"
URL = f"https://x.com/search?q="

"""
options = Options()

options.binary_location = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'

service = Service(executable_path='./chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)
"""

service = Service(executable_path='./geckodriver')
driver = webdriver.Firefox(service=service)


def login():
    driver.get("https://x.com/login")
    time.sleep(15)

    username_input = driver.find_element(By.XPATH, "//input[@autocomplete='username']")
    username_input.send_keys(username)
    username_input.send_keys(Keys.ENTER)

    time.sleep(2)

    password_input = driver.find_element(By.XPATH, "//input[@autocomplete='current-password']")
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    time.sleep(2)

    if "home" in driver.current_url:
        print("Login successful")
    else:
        print("Login failed")



def main():
    dataframe = {
        "url": [],
        "model": [],
        "review": [],
        "data": [],
        "pos": [],
        "neg": []
    }

    
    
    login()

    for gm_model in gm_models:
        for query in QUERYS:
            search_url = f"{URL}{gm_model.replace(' ', '%20')}%20{query}{FILTER}"
            print(f"Searching for: {search_url}")
            try:
                driver.get(search_url)
            except Exception as e:
                print(f"Error accessing search URL: {e}")
                continue
            time.sleep(5)

            last_height = driver.execute_script("return document.body.scrollHeight")
            scholl_height = 0

            tweets_history = []

            while True:
                scholl_height += 500 

                driver.execute_script(f"window.scrollTo(0, {scholl_height});")
                time.sleep(0.5)
                last_height = driver.execute_script("return document.body.scrollHeight")

                if scholl_height >= last_height or scholl_height >= 10000:
                    break

                print(f"Scrolled to height: {last_height}, current scroll height: {scholl_height}")


                try:
                    
                    show_more_buttons = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="tweet-text-show-more-link"]'))
                    )

                    if show_more_buttons:
                        for button in show_more_buttons:
                            try:
                                button.click()
                                time.sleep(1)
                            except Exception as e:
                                print(f"Error clicking show more button: {e}")
                except Exception as e:
                    pass
                tweets = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="tweetText"]'))
                )

                tweets_datas = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//time'))
                )


                for tweet, data in zip(tweets, tweets_datas):
                    try:
                        text = tweet.text.strip().replace("\n", " ").replace("\t", " ")
                    except Exception as e:
                        print(f"Error getting tweet text: {e}")
                        continue
                    translate = text

                    try:
                        translate = GoogleTranslator(source='auto', target='portuguese').translate(text)
                    except Exception as e:
                        print(f"Error translating tweet: {e}")

                    clean_review = sentimentAnalysis.remove_swearword(translate)

                    if clean_review is None and clean_review in tweets_history:
                        continue
                    
                    print(f"Review: {clean_review}")
                    tweets_history.append(clean_review)
                    sentiment_scores = sentimentAnalysis.analyze_sentiment(clean_review)

                    datetime = ""
                    try:
                        datetime = data.get_attribute("datetime")
                    except Exception as e:
                        print(f"Error getting datetime: {e}")

                    dataframe["url"].append(str(driver.current_url))
                    dataframe["model"].append(str(gm_model))
                    dataframe["review"].append(str(translate))
                    dataframe["data"].append(str(datetime))
                    dataframe["pos"].append(str(sentiment_scores["pos"]))
                    dataframe["neg"].append(str(sentiment_scores["neg"]))

                    df = pd.DataFrame(dataframe)

                    # Put in https://upb1od2ypa.execute-api.us-east-1.amazonaws.com/hml/ra-bucket-381492149341/{filename} with file
                
                    filename = f"tweets_{gm_model.replace(' ', '_')}_{query}.csv"

                    requests.put(
                        f"https://upb1od2ypa.execute-api.us-east-1.amazonaws.com/hml/ra-bucket-381492149341/{filename}",
                        data=df.to_csv(index=False),
                        headers={"Content-Type": "text/csv"}
                    )


    driver.quit()

main()
