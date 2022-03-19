from functions import *
from flask import Flask,render_template
from flask import request as f_request


app=Flask(__name__)
@app.route("/",methods=["GET","POST"])
def request():
    global user_name
    if f_request.method== "POST":
        req = f_request.form
        user_name=req["user_name"]
        msg=req["msg_data"]
        request_help(user_name)
        r.publish('ch-1',msg)


    return render_template("UserPage.html")


@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    global user_name,num_of_travellers,destination_city,trip_status,user_radius,user_message_recieved
    nearest_cars={}
    user_message_recieved = r.lpop('msg_scoreboard')
    if f_request.method == "POST":

        req = f_request.form
        user_name= req["user"]
        num_of_travellers=req["Number of travellers"]
        destination_city=req['destination_city']
        trip_status=req["trip status"]
        user_radius=req["radius"]

        nearest_cars=get_nearest_cars(user_name, num_of_travellers, destination_city,
                                      trip_status,user_radius)


    return render_template("HelpDesk.html", user_name=user_name, nearest_cars=nearest_cars,user_message_recieved=user_message_recieved)


if __name__=='__main__':
    app.run(debug=True)

