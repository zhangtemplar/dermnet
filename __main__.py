import os
from selenium import webdriver
from urllib import urlretrieve
import cPickle
from time import sleep
from random import randint

ROOT_URL = 'http://www.dermnet.com/dermatology-pictures-skin-disease-pictures/'
DATA_PATH = '/Users/zhangqiang/Downloads/dermnet'


def main():
    driver = webdriver.Chrome("/Users/zhangqiang/chromedriver")
    categoryLinks = getCategories(driver)
    sleep(randint(0, 6000) / 1000.0)
    for categoryLink in categoryLinks:
        print categoryLink['name'], categoryLink['url']
        imageLinks = getImages(driver, categoryLink['url'], categoryLink['name'])
        sleep(randint(0, 6000) / 1000.0)
        for imageLink in imageLinks:
            print imageLink['name'], imageLink['url']
            getImage(driver, imageLink['url'], categoryLink['name'], imageLink['name'])
            sleep(randint(0, 1000) / 1000.0)


def getImages(driver, categoryLink, categoryName):
    imageLinks = loadCheckpoints(categoryName + ".cp")
    if imageLinks is not None:
        return imageLinks
    driver.get(categoryLink)
    while True:
        elements = driver.find_elements_by_xpath('//*[@id="container"]/div[3]/div[1]/div[3]/div/a')
        imageLinks = []
        for element in elements:
            link = element.get_attribute("href")
            try:
                nameElement = element.find_element_by_xpath('div[@class="name"]')
                name = nameElement.text
            except Exception as e:
                name = element.get_attribute("name")
            try:
                descriptionElement = element.find_element_by_xpath('div[@class="desc"]')
                description = descriptionElement.text
            except Exception as e:
                description = name
            imageLinks.append({
                'name': description,
                'description': name,
                'url': link
            })
        if not nextPage(driver):
            break
    saveCheckpoints(imageLinks, categoryName + ".cp")
    return imageLinks


def getImage(driver, imageLink, categoryName, imageName):
    imagePath = os.path.join(DATA_PATH, categoryName + "-" + imageName)
    if os.path.exists(imagePath):
        return
    driver.get(imageLink)
    image = driver.find_element_by_xpath('//*[@id="disImg"]')
    link = image.get_attribute("src")
    urlretrieve(link, imagePath)


def nextPage(driver):
    try:
        nextButton = driver.find_element_by_xpath('//*[@id="container"]/div[3]/div[1]/div[3]/div[1]/div/a[last()]')
        nextButton.click()
        return True
    except Exception as e:
        print 'next button is found', e
    return False


def loadCheckpoints(filePath):
    if os.path.exists(filePath):
        data = cPickle.load(open(filePath, 'rb'))
        return data
    else:
        return None


def saveCheckpoints(data, filePath):
    cPickle.dump(data, open(filePath, 'wb'))


def getCategories(driver):
    categoryLinks = loadCheckpoints("category.cp")
    if categoryLinks is not None:
        return categoryLinks
    driver.get(ROOT_URL)
    categoryElements = driver.find_elements_by_xpath('//*[@id="container"]/div[3]/div[1]/table/tbody/tr[2]/td/a')
    categoryLinks = []
    for element in categoryElements:
        title = element.text
        link = element.get_attribute("href")
        print title, link
        categoryLinks.append({'name': title, 'url': link})
    saveCheckpoints(categoryLinks, "category.cp")
    return categoryLinks


if __name__ == '__main__':
    main()