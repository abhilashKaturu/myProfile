import pyowm
import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session, current_app
from flask_session import Session
from tempfile import mkdtemp

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# # # # Custom filter
# # # # app.jinja_env.filters["usd"] = usd


@classmethod
def setUpClass(self):
    self.app = create_app("testing")
    self.client = self.app.test_client()


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/", methods=["GET", "POST"])
def index():
    session["location"] = "District of Columbia"
    if request.method == "POST":
        loc = request.form.get('find-location')
        
        x = do_stuff(loc)
        
        if x == False:
            return render_template('index.html', loc = session["location"].title(), details=do_stuff(session["location"]), flag=True, ot = oth_tmp())
        
        else:
            session["location"] = loc
            
            return render_template('index.html', details=x, loc=loc.title(), ot=oth_tmp())
    else:
        return render_template('index.html', details=do_stuff(session["location"]), loc=session["location"].title(), ot=oth_tmp())

def do_stuff(loc):

    #Providing API Key
    owm = pyowm.OWM('a0211c741af8fefb7ceff2307e6e2513')

    try:
        city = loc

        #Creating Shortcuts
        y = owm.weather_manager()

        x = y.weather_at_place(city)

    except:
        return False

    w = x.weather

    tmp = w.temperature('fahrenheit')

    wi = w.wind()

    return {'wind_speed': wi['speed'], 'feels_like': round(tmp['feels_like']), 'max': round(tmp['temp_max']), 'min': round(tmp['temp_min']), 'temp': round(tmp['temp']), 'humidity': w.humidity, 'loc': loc}

def oth_tmp():
    #Providing API Key
    owm = pyowm.OWM('a0211c741af8fefb7ceff2307e6e2513')

    thing = {}

    idk = ['New York', 'Los Angeles', 'Mumbai', 'London']

    for i in range(4):

        try:
            city = idk[i]

            #Creating Shortcuts
            y = owm.weather_manager()

            x = y.weather_at_place(city)

        except:
            return False

        w = x.weather

        tmp = w.temperature('fahrenheit')

        thing[city] = round(tmp['temp'])
    
    return thing



    

if __name__ == "__main__":
    app.run()
