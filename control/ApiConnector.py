import requests

class ApiConnector():
    def __init__(self, url, number=2):
        self.number = number
        self.url = url

class spoonacularApiConnector(ApiConnector):

    def __init__(self, url, number=2, apiKey="?apiKey=c917e235c7cd4c389ffc901c220f86d8"):
        super().__init__(url, number=number)
        self.apiKey = "?apiKey=c917e235c7cd4c389ffc901c220f86d8"

    def complexSearch(self, query, parameters):
        string = self.url + "recipes/complexSearch" + self.apiKey + "&query=" + query

        for parameter in parameters:
            string = string + "&" + parameter

        string = string + "&number="+str(self.number)

        response = requests.get(string)
        print("sending request: " + string)
        print(response.content)



def main():
   con = spoonacularApiConnector("https://api.spoonacular.com/")
   for i in range(100):
    con.complexSearch("burrito", ["addRecipeInformation=true"])


if __name__ == "__main__":
    main()
