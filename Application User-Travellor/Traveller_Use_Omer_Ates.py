
import redis as rd
from pymongo import MongoClient
import numpy as np
from datetime import datetime,timedelta
from geopy.distance import geodesic
import folium
import webbrowser
from pymongo import MongoClient
#DataBases connection with MongoDbAtlas and Redis
client = MongoClient("mongodb+srv://mongo:omer123@cluster0.kmfv3.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
r=rd.Redis('127.0.0.1')


user_name_traveller='jhaacker0'



#Collecting data from MongoDb Traveller Colllection
def get_traveller_info(user_name_traveller)-> tuple:
    source_lat,source_lng,dest_lat,dest_lng = 0,0,0,0
    db = client.yellow
    collection_traveller= db['traveller']
    quary = {'username': f'{user_name_traveller}'}
    doc = collection_traveller.find(quary)

    source_lat=float(doc[0]['latitude'])
    source_lng=float(doc[0]['longtitude'])
    dest_lat=float(doc[0]['seclatitude'])
    dest_lng=float(doc[0]['seclongtitude'])
    traveller_dest_city=doc[0]['dest_city']
    traveller_starting_city=doc[0]["city"]

    return traveller_starting_city,source_lat,source_lng,traveller_dest_city

#Get Nearest car from MongoDb Atlas Collection and collecting that data in dictionary
def get_nearest_cars(user_name_traveller,traveller_dest_city):

    db = client.yellow
    collection_cars= db['car']
    quary = {'dest_city': f'{traveller_dest_city}'}
    doc = collection_cars.find(quary)

    pipe=r.pipeline()
    for i in doc:
        lat=float(i['latitude'])
        lng=float(i['longtitude'])
        pipe.geoadd('points',[lng,lat,i['username']])
    pipe.execute()
    nearest_cars = dict()
    closest_cars = r.georadiusbymember(name="points", member=user_name_traveller, radius=20, unit='km', withcoord=True)

    for i in closest_cars:
        dist=r.geodist(name="points",place1=user_name_traveller,place2=i[0].decode("utf-8"),unit="km")
        nearest_cars[i[0].decode("utf-8")] = f"{dist} km"

    return nearest_cars

traveller_starting_city,source_lat,source_lng,traveller_dest_city=get_traveller_info(user_name_traveller)
print(user_name_traveller,traveller_starting_city,traveller_dest_city)

nearest_cars=get_nearest_cars(user_name_traveller,traveller_dest_city)

print(nearest_cars)



#Chosing nearest car in our nearest_car dictionary
user_name_car = None
min_distance = None

for name, dist in nearest_cars.items():

    if isinstance(dist, str):
        dist=float(dist.split(' ')[0])

    if name != user_name_traveller:

        if user_name_car is None:
            user_name_car = name
            min_distance = dist

        if dist < min_distance:
            min_distance = dist
            user_name_car = name

print(user_name_car, min_distance)


#user_name_car="aschoenrockna"
def get_car_info(user_name_car):

    db = client.yellow
    collection_cars = db['car']
    quary = {'username': f'{user_name_car}'}
    doc = collection_cars.find(quary)

#Collecting nearest car information
    speed=float(doc[0]["speed"])
    departure_time=datetime.strptime(doc[0]["time"],"%H:%M")
    lat = float(doc[0]['latitude'])
    lng = float(doc[0]['longtitude'])
    dest_lat = float(doc[0]['seclatitude'])
    dest_lng = float(doc[0]['seclongtitude'])


    return speed,departure_time,lat,lng,dest_lat,dest_lng

speed,departure_time,lat,lng,dest_lat,dest_lng=get_car_info(user_name_car)
print(user_name_car,speed,departure_time.time(),lat,lng,dest_lat,dest_lng)

#Calculating distance from starting point and last point
coordinates=(lat, lng,dest_lat,dest_lng)
def get_distance(coordinates):
    lat, lng, dest_lat, dest_lng=coordinates

    distance=geodesic((lat, lng) ,(dest_lat,dest_lng))
    return distance


distance=get_distance(coordinates)
print("Distance between two city:",distance)


#Calculating total travel hours distance and estimation time arrivals
travel_times=timedelta(hours=distance.km/speed)
arrival_time=departure_time+travel_times
print("Departure Time:",departure_time.time())
print("Total Travel Time:",travel_times)
print("Arrival Time:",arrival_time.time())


#Collecting coordinates for traveller ,cars starting point and destination city
traveller=(source_lat),(source_lng)
location_car_first=(lat),(lng)
departure_point=(dest_lat),(dest_lng)

#Creating map and opening in browser above information
m = folium.Map(location=traveller,width=800,height=400)
folium.Marker(traveller,popup="TRAVELLER").add_to(m)
folium.Marker(location_car_first,popup="CAR STARTING POINT",tooltip=speed).add_to(m)
folium.Marker(departure_point,popup=arrival_time.time(),tooltip=distance).add_to(m)
folium.PolyLine((location_car_first,departure_point)).add_to(m)
m
m.save("map.html")
webbrowser.open("map.html")




