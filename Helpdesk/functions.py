import random
import redis
from pymongo import MongoClient
#client = MongoClient("mongodb+srv://sasha:sasha123@cluster0.kmfv3.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
client = MongoClient('localhost:27017')
r=redis.Redis('127.0.0.1')

r.flushdb()

global user_name,num_of_travellers,destination_city,trip_status,user_radius,user_message_recieved
user_name='No User'
num_of_travellers=0
destination_city=''
trip_status='ongoing'
user_radius=0
user_message_recieved=''

#User Requests for help
def request_help(user_name)-> tuple:
    source_lat,source_lng,dest_lat,dest_lng = 0,0,0,0
    #Gets user travel info from mongo DB
    db = client.mydb
    collection_traveller= db['traveller']
    query = {'username': f'{user_name}'}
    doc = collection_traveller.find(query)
    for i in doc:
        source_lat=float(i['latitude'])
        source_lng=float(i['longtitude'])
        dest_lat=float(i['seclatitude'])
        dest_lng=float(i['seclongtitude'])
        dest_city=i['dest_city']

    #Generates random point in the travel route to simulate car crash location:

    incedent_lat=round(random.uniform(source_lat, dest_lat), 6)
    incedent_lng=round(random.uniform(source_lng, dest_lng), 6)
    r.delete("points")
    r.geoadd("points", [incedent_lng,incedent_lat,user_name])
    return user_name,incedent_lat,incedent_lng

def get_nearest_cars(user_name, num_of_travellers, destination_city, trip_status,user_radius):
    print(user_name, num_of_travellers, destination_city, trip_status,user_radius)
    doc=mongoQuery(num_of_travellers,destination_city,trip_status)
    #load all cars from mongoDB car collection to redis points GeoSpatial sorted set:
    pipe=r.pipeline()
    for i in doc:
        lat=float(i['latitude'])
        lng=float(i['longtitude'])
        pipe.geoadd('points',[lng,lat,i['username']])
    pipe.execute()
    #finds nearest cars to user and stores it in dictionary  called nearest_cars
    nearest_cars = dict()
    closest_cars = r.georadiusbymember(name="points", member=user_name, radius=user_radius,
                                            unit='km', withcoord=True)

    for i in closest_cars:

        dist=r.geodist(name="points",place1=user_name,place2=i[0].decode("utf-8"),unit="km")
        if dist==0:
            continue
        nearest_cars[i[0].decode("utf-8")] = f"{dist} km"
        if len(nearest_cars)>10:
            break
    return nearest_cars

def mongoQuery(num_of_travellers,destination_city,trip_status):
    db = client.mydb
    collection_trip = db['trip']
    collection_car = db['car']

    result = collection_car.aggregate([
        {"$lookup": {

            "from": "trip",
            "localField": "username",
            "foreignField": "car_username",
            "as": "trip_data"
        }
        },
        {"$match":{
        "trip_data.traveller": {"$size": int(num_of_travellers)},
        "dest_city": f"{destination_city}",
        "trip_data.trip_status": f"{trip_status}"
    }

        }])

    return result

