import urllib.request, urllib.error, urllib.parse, json

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request." )
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None


baseurl = "https://acnhapi.com/v1/"

# Returns a dictionary of all the villagers in Animal Crossing
def get_all_villagers():
    # Make header for request
    headers = {"User-Agent":"Kelly acnh page (ktong3@uw.edu)"}
    req = urllib.request.Request(baseurl + "villagers/", headers=headers)

    # Create a string url
    response_str = safe_get(req).read()

    # Converting a JSON string to a dictionary
    data = json.loads(response_str)
    return data

# Store all villagers data in a variable
villagers = get_all_villagers()


# Villager Class
class Villager():
    """A class to represent a villager"""

    def __init__(self, dict):
        self.id = dict["id"]
        self.name = dict["name"]["name-USen"]
        self.personality = dict["personality"]
        self.birthday = dict["birthday-string"]
        self.species = dict["species"]
        self.gender = dict["gender"]
        self.phrase = dict["saying"]
        self.hobby = dict["hobby"]

    def make_photo_url(self):
        url = "{}images/villagers/{}".format(baseurl, self.id)
        return url

    def __str__(self):
        """String rep of villager information"""
        name = "Name : {}".format(self.name) + "\n"
        personality = "Personality : {}".format(self.personality) + "\n"
        bday = "Birthday : {}".format(self.birthday) + "\n"
        species = "Species : {}".format(self.species) + "\n"
        gender = "Gender : {}".format(self.gender) + "\n"
        phrase = "Phrase : {}".format(self.phrase)
        return name + personality + bday + species + gender + phrase


# Checks if name is a valid Animal Crossing villager
def check_villager(name):
    for animal in villagers:
        if name in villagers[animal]["name"].values():
            return True
    return False


# Returns a Villager class with the specified name
def get_villager_info(name):
    dict = {}

    for animal in villagers:
        if name == villagers[animal]["name"]["name-USen"]:
            dict = villagers[animal]

    villager = Villager(dict)
    return villager


# months - list(string) of months
# Returns dictionary of all villagers by specified months
def search_birthday(months):
    dict = {}

    for month in months:
        for animal in villagers:
            birth_month = villagers[animal]["birthday-string"].split()[0]
            if month == birth_month:
                # add new key and value(dict of info)
                dict[animal] = villagers[animal]
    return dict


from flask import Flask, render_template, request
import logging

app = Flask(__name__)

@app.route("/")
def main_handler():
    app.logger.info("In MainHand®ler")
    return render_template("home.html")

# User input - type villager name and output the villager's information
@app.route("/gresponse", methods=['POST'])
def get_villager():
    name = request.form.get("villager_name")
    app.logger.info(name)

    if check_villager(name):
        villager = get_villager_info(name)
        return render_template("results.html", villager=villager)
    else:
        return render_template("home.html", page_title="Search Error",
                                prompt="The villager does not exist or you need"
                                       " to capitalize the first letter. Try "
                                       "again.")

# User input - birth month check box and output villagers by selected months
@app.route("/birthday", methods=['POST'])
def birthdays():
    birth_months = request.form.getlist("birth_month")
    app.logger.info(birth_months)

    if birth_months:
        dict = search_birthday(birth_months)
        villager_list = []

        for animal in dict:
            name = dict[animal]["name"]["name-USen"]
            villager = get_villager_info(name)
            villager_list.append(villager)

        return render_template("birthdays.html", villagers=villager_list,
                               birthdays = birth_months)
    else:
        return render_template("home.html", page_title="Search Error",
                                prompt="Please select at least one month.")

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)