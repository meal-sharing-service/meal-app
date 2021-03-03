import requests
import json


class ApiConnector():
    def __init__(self, url, number=2):
        self.number = number
        self.url = url


class spoonacularApiConnector(ApiConnector):

    def __init__(self, url, number=2, apiKey="?apiKey=e6dd71bc643e4baca4fb9c8cfab6f668"):
        super().__init__(url, number=number)
        self.apiKey = "?apiKey=e6dd71bc643e4baca4fb9c8cfab6f668"

    def complexSearch(self, query, parameters):
        string = self.url + "recipes/complexSearch" + self.apiKey + "&query=" + query

        for parameter in parameters:
            string = string + "&" + parameter

        string = string + "&number=" + str(self.number)

        response = requests.get(string)
        print("sending request: " + string)
        return response.content


def main():
    con = spoonacularApiConnector("https://api.spoonacular.com/")
    resp = None
    for i in range(1):
        resp = con.complexSearch("burrito", ["addRecipeInformation=true"])
    data = json.loads(resp.decode("utf-8"))
    cuisines = data['results'][0]['cuisines']
    id = data['results'][0]['id']
    #calories = data['results'][0]['calories']
    summary = data['results'][0]['summary']
    print(data)
    vegetarian = data['results'][0]['vegetarian']
    vegan = data['results'][0]['vegan']
    glutenFree = data['results'][0]['glutenFree']
    dairyFree = data['results'][0]['dairyFree']

    allergyDict = {"vegan": vegan,
                   "vegetarian": vegetarian,
                   "glutenFree": glutenFree,
                   "dairyFree": dairyFree}

    print(allergyDict)

    print(summary)
    instructions = ""
    ingredient_ids = []
    ingredient_names = []
    cuisines = data['results'][0]['cuisines']

    for inst in data['results'][0]['analyzedInstructions'][0]['steps']:
        instructions = instructions + inst['step']
        for ing in inst['ingredients']:
            if ing['id'] not in ingredient_ids:
                ingredient_ids.append(ing['id'])
                ingredient_names.append(ing['name'])

    print(ingredient_names)



if __name__ == "__main__":
    main()
