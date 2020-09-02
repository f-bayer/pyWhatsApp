"""
This is a small, fun script that replies "Doch" every time a specified user writes "Nein" in WhatsApp
(and the other way around).
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

import time

def read_last_in_message(driver, counted_strings = None):
    """
    Reading the last message that you got in from the chatter
    """
    if not counted_strings:
        counted_strings = []

    counts = dict()
    for tpl in counted_strings:
        counts[tpl] = 0
    message = ''
    emojis = []
    continuous = True
    previous = None
    for messages in driver.find_elements_by_xpath(
            "//div[contains(@class,'message-in')]"):
        try:
            message = ""
            emojis = []

            message_container = messages.find_element_by_xpath(
                ".//div[@class='copyable-text']")

            message = message_container.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
            ).text

            for emoji in message_container.find_elements_by_xpath(
                    ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
            ):
                emojis.append(emoji.get_attribute("data-plain-text"))

            found_any = False
            for tpl in counted_strings:
                found = False
                for search_string in tpl:
                    if search_string in message:
                        found = True
                        found_any = True
                        break
                if found:
                    counts[tpl] += 1
                    if continuous and previous == None:
                        previous = tpl
                    elif previous != tpl:
                        continuous = False
                else:
                    counts[tpl] = 0
            if not found_any:
                continuous = False

        except NoSuchElementException:  # In case there are only emojis in the message
            try:
                message = ""
                emojis = []
                message_container = messages.find_element_by_xpath(
                    ".//div[@class='copyable-text']")

                for emoji in message_container.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                ):
                    emojis.append(emoji.get_attribute("data-plain-text"))
            except NoSuchElementException:
                pass

    return message, counts, continuous

def read_last_out_message(driver):
    """
    Reading the last message that you wrote
    """
    message = ""
    emojis = []
    for messages in driver.find_elements_by_xpath(
            "//div[contains(@class,'message-out')]"):
        try:
            message = ""
            emojis = []

            message_container = messages.find_element_by_xpath(
                ".//div[@class='copyable-text']")

            message = message_container.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
            ).text

            for emoji in message_container.find_elements_by_xpath(
                    ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
            ):
                emojis.append(emoji.get_attribute("data-plain-text"))

        except NoSuchElementException:  # In case there are only emojis in the message
            try:
                message = ""
                emojis = []
                message_container = messages.find_element_by_xpath(
                    ".//div[@class='copyable-text']")

                for emoji in message_container.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                ):
                    emojis.append(emoji.get_attribute("data-plain-text"))
            except NoSuchElementException:
                message = []
                pass

    return message, emojis


answers = {('Nein', 'nein'): 'Doch.', ('Doch', 'doch'): 'Nein.'}
with webdriver.Firefox() as driver:

    driver.get('https://web.whatsapp.com')
    wait = WebDriverWait(driver, 10)
    print(driver.session_id)
    print(type(driver.session_id))
    print(driver.command_executor._url)
    print('Please make sure to be logged into WhatsApp Web before proceeding with the inputs.')
    cont = 'y'
    targets = []
    while cont != 'n':
        friend_name = input('Please enter name of friend to be spammed: ')
        target = '"' + friend_name + '"'
        print(target)
        targets.append(target)
        cont = input('Add another friend to target list? (y/n) ')

    while True:
        for target in targets:
            x_arg = '//span[contains(@title,' + target + ')]'
            try:
                group_title = wait.until(EC.presence_of_element_located((
                    By.XPATH, x_arg)))
                group_title.click()
            except TimeoutException:
                print(target, 'timed out.')

            # inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
            # inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
            # inp_xpath = '//div[@class="_2S1VP copyable-text selectable-text"][@contenteditable="true"][@data-tab="1"]'
            inp_xpath = '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]'

            # read last message
            message, counts, continuous = read_last_in_message(driver, answers.keys())

            for tpl in counts.keys():
                if counts[tpl] > 0:
                    input_box = driver.find_element_by_xpath(inp_xpath)
                    time.sleep(2)
                    message_out, _ = read_last_out_message(driver)
                    # Easter egg: Give up if all the messages are stubborn
                    if continuous:
                        if not 'You win' in message_out:
                            input_box.send_keys("You have been stubborn for at least "+str(counts[tpl])+" turns. " +
                                                "I am not able to load more messages. You win." + Keys.ENTER)
                            time.sleep(2)
                    else:
                        answer = answers[tpl] + ' (' + str(counts[tpl]) + ')'
                        if answer != message_out:
                            input_box.send_keys(answer + Keys.ENTER)
                            time.sleep(2)
                    break



