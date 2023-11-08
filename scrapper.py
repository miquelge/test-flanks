import json
import os

import requests
from bs4 import BeautifulSoup

URLRecetasGratis = 'https://www.recetasgratis.net'
FacebookSharing = 'facebook'
TwitterSharing = 'twitter'
PinterestSharing = 'pinterest'
WhatsappSharing = 'whatsapp'

linksToProcess = [URLRecetasGratis]
linksToProcessSet = set(linksToProcess)

DB_URL = 'http://localhost:5000'
DB_URL_RECIPE = DB_URL + '/recipe'

AMOUNT_RECIPES_STORED = 0


class Recipe:
    def __init__(self, title, introduction, url, diners, duration, difficulty, ingredients, steps):
        self.title = title
        self.introduction = introduction
        self.url = url
        self.diners = diners
        self.duration = duration
        self.difficulty = difficulty
        self.ingredients = ingredients
        self.steps = steps

    def print(self):
        print(self.title)
        print(self.introduction)
        print(self.url)
        print(self.diners)
        print(self.duration)
        print(self.difficulty)
        print('Ingredients:')
        for i in self.ingredients:
            print('    ' + i)
        print('Steps: ')
        for step in self.steps:
            print(step)

    def json(self):
        return {
            'title': self.title,
            'introduction': self.introduction,
            'url': self.url,
            'diners': self.diners,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'ingredients': self.ingredients,
            'steps': self.steps
        }

def request(method, URL, body = {}):
    if method == 'GET':
        response = requests.get(URL, json=body)
    elif method == 'POST':
        response = requests.post(URL, json=body)
    elif method == 'DELETE':
        response = requests.delete(URL, json=body)

    if (not response):
        print('An error has occurred.')
    return response

def isShareableLink(URL):
    return (
        URL.find(FacebookSharing) != -1 or
        URL.find(TwitterSharing) != -1 or
        URL.find(PinterestSharing) != -1 or
        URL.find(WhatsappSharing) != -1
    )

def isPrintingLink(URL):
    return URL.find('?print') != -1

def isDownloadLink(URL):
    return URL.find('download') != -1

def isUserLink(URL):
    return URL.find('/usuarios') != -1

def isGoodLink(URL):
    return (
        URL.find(URLRecetasGratis) != -1 and
        not isShareableLink(URL) and
        not isPrintingLink(URL) and
        not isDownloadLink(URL) and
        not isUserLink(URL)
    )

def isRecipeURL(URL):
    return (
        URL.find(URLRecetasGratis + '/receta') != -1 and 
        URL.find(URLRecetasGratis + '/recetas') == -1
    )

def hasBeenStored(URL):
    response = request('GET', DB_URL_RECIPE, {'url': URL})
    responseAsJson = json.loads(response.text)
    l = responseAsJson['content']
    return len(l) >= 1

def findAllWebsiteLinks(soup):
    linkContainers = soup.find_all('a', href=True)
    for container in linkContainers:
        link = container['href']
        if isGoodLink(link) and (link not in linksToProcessSet):
            linksToProcessSet.add(link)
            linksToProcess.append(link)

def storeRecipe(recipe):
    print('    New recipe: ' + recipe.title)
    response = request('POST', DB_URL_RECIPE, recipe.json())
    global AMOUNT_RECIPES_STORED
    AMOUNT_RECIPES_STORED = AMOUNT_RECIPES_STORED + 1
    print('    ' + str(AMOUNT_RECIPES_STORED) + ' stored recipe(s)')

def removeEmptyLines(text):
    return os.linesep.join([s for s in text.splitlines() if s])

def retrieveStep(content):
    # print(content)
    orderDiv = content.find('div', class_='orden')
    if (orderDiv):
        order = orderDiv.text
        p = content.find('p')
        stepText = ''
        if hasattr(p, 'text'):
            stepText = content.find('p').text
        # print(order)
        # print(stepText)
        return "".join([order, '\n', stepText])
    else:
        return None

def retrieveRecipe(soup, URL):
    body = soup.body
    container = body.find('div', class_='container')
    header_gap = container.find('div', class_='header-gap')
    article = header_gap.find('article', class_='columna-post')
    title = article.find('h1', class_='titulo--articulo').text
    # print(title)

    introParagraphs = article.find('div', class_='intro').find_all('p')
    introduction = ''
    for p in introParagraphs:
        introduction += p.text
    # print(introduction)

    recipeInfo = article.find('div', class_='recipe-info')

    auxDiners = recipeInfo.find('span', class_='comensales')
    if hasattr(auxDiners, 'text'):
        diners = auxDiners.text
    else:
        diners = None
    # print(diners)

    auxDuration = recipeInfo.find('span', class_='duracion')
    if hasattr(auxDuration, 'text'):
        duration = auxDuration.text
    else:
        duration = None
    # print(duration)

    auxDifficulty = recipeInfo.find('span', class_='dificultad')
    if hasattr(auxDifficulty, 'text'):
        difficulty = auxDifficulty.text
    else:
        difficulty = None
    # print(difficulty)

    ingredientsList = recipeInfo.find_all('li', class_='ingrediente')
    ingredients = []
    for i in ingredientsList:
        text = removeEmptyLines(i.text)
        ingredients.append(text)
    # print(ingredients)

    recipeStepsContainer = article.find('div', class_='p402_premium')
    recipeSteps = recipeStepsContainer.find_all('div', class_='apartado')
    steps = []
    for step in recipeSteps:
        newStep = retrieveStep(step)
        if (newStep):
            steps.append(newStep)
    # print(steps)
    
    newRecipe = Recipe(title, introduction, URL, diners, duration, difficulty, ingredients, steps)
    # newRecipe.print()
    storeRecipe(newRecipe)
        
def processLink(URL):
    print('Processing: ' + URL)
    response = request('GET', URL)
    if (response):
        soup = BeautifulSoup(response.content, 'html.parser')
        if isRecipeURL(URL) and not hasBeenStored(URL):
            retrieveRecipe(soup, URL)
        findAllWebsiteLinks(soup)

if __name__ == '__main__':
    for link in linksToProcess:
        processLink(link)
