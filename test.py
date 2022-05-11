from operator import itemgetter
from flask import Flask,request
import math
import json

app = Flask(__name__)

def read_json():

    '''
        This function reads a file in the same directory of this file
        and the name "cities-canada-usa.json" and returns a dict 
        object with all the data in the file
    '''
    with open("cities-canada-usa.json", encoding="utf-8") as file:
        return(json.loads(file.read()))

def distance_between_two_points(x1,y1,x2,y2):

    '''
    This functions get 2 points (x,y) and returns the distance
    between them.
    '''
    return math.sqrt(math.pow(float(x1)-float(x2),2) + math.pow(float(y1)-float(y2),2))

@app.route('/api/search',methods=["GET"])
def search():

    '''
    This endpoint/function get the parameters q, latitude and longitude 
    in the url body. Then iterates in the dict object of the json file
    to search similarities between the q argument and the name of the city.
    When a city is similar to the word, it calculates the distance of both
    coordinates and if it is not too far, the function adds it to an array.
    It returns 400 error if any of the arguments is missing or if you 
    give an incorrect data type.
    '''

    try:

        word = request.args["q"]
        lat = request.args["latitude"]
        lon = request.args["longitude"]
    
        jsonDict = read_json()
        finalArr = []

        for elem in jsonDict:
            if word.lower() in elem["name"].lower():

                try:
                    latitude = elem["lat"]
                    longitude = elem["long"]
                    #The calculation of the score is the next:
                    #The coordinates are used as in a cartesian coordinate system. So if you want
                    #to get the distance between 2 points, you use the formula ((x1-x2)^2 + (y1-y2)^2)^1/2
                    #
                    #Because the score has to be between 0.0 and 1.0, 10 is taken as the upper distance limit.
                    #So, if the distance is greater than 10, the city is omitted. If not, it is included in the
                    #final array. 
                    #
                    #Now to calculate the score, I use the distance (that has to be beetween 0.0 and 10.0 inclusive).
                    #and divide it by 10. Now we get a number between 0 and 1. But because the 1 is more confident,
                    #I substract 1 - distance/10 to get the score
                    #
                    #Also for more precision, I use 2 decimals in score

                    score = round(1 - distance_between_two_points(lat,lon,elem["lat"],elem["long"])/10,2)
                    score1 = distance_between_two_points(lat,lon,elem["lat"],elem["long"])
                except:
                    return "Invalid type on given arguments", 400

                if score1 <= 10:

                    arr = {
                        "name":elem["name"] +", "+ elem["admin1"] +", "+ elem["country"],
                        "latitude":latitude,
                        "longitude":longitude,
                        "score":score,
                    }
                    finalArr.append(arr)                

        #When the search of the near cities is finished, it is sorted by score and 
        #stored in the final dict, it also returns and empty list if no cities
        #are near the given coordinates

        finalDict = {
            "search":[]
        }


        finalArr = sorted(finalArr, key=itemgetter('score'), reverse=True)

        finalDict["search"] = finalArr
        return finalDict

    except:
        return "You probably missed an argument or give an invalid argument(q,latitude,longitude)", 400
        
#This was made to run the flask server on the port 5000. Debug mode is disabled
if  __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
    print("API started")