import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, hasNumbers

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    aDict = db.execute('SELECT stock, shares FROM current WHERE personid = :id', id = session["user_id"])
    
    update_cash = 0
    
    for i in range(len(aDict)):
        
        bDict = lookup(aDict[i]["stock"])
        
        aDict[i]["price"] = usd(float(bDict["price"]))
        
        aDict[i]["total"] = usd(float(bDict["price"]) * float(aDict[i]["shares"]))
        
        update_cash += float(bDict["price"]) * float(aDict[i]["shares"])
        
        aDict[i]['name'] = bDict['name']
    
    update_cash = 10000 - update_cash
    
    db.execute('UPDATE users SET cash = :cash WHERE id = :id', cash = update_cash, id = session["user_id"])
    
    return render_template('index.html', ttl_cash = usd(float(update_cash)), aDict = aDict)
    












@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        
        if lookup(request.form.get('symbol')) == None:
            return render_template("buy.html", msg = "Invalid Stock")
        
        amount_left = db.execute(f"SELECT cash FROM users WHERE id = {session['user_id']}")
        
        amount_left = amount_left[0]['cash']
        
        aDict = lookup(request.form.get('symbol'))
        
        price = float(aDict['price']) * float(request.form.get('shares'))
        
        if amount_left < price:
            return render_template("buy.html", msg = "You can't afford that; You're broke")
        
        else:
            cash = amount_left - price
            
            db.execute('UPDATE users SET cash = :cash WHERE id = :id', cash = cash, id = session['user_id'])
            
            db.execute('INSERT INTO history (personid, stock, shares, price) VALUES (:id, :symbol, :shares, :price)', id = session["user_id"], symbol = aDict["symbol"], shares = request.form.get('shares'), price = price)
            
            previous_shares = db.execute('SELECT shares FROM current WHERE personid = :id AND stock = :stock', id = session['user_id'], stock = aDict["symbol"])
            
            try:
                previous_shares = int(previous_shares[0]["shares"])
                
                db.execute('UPDATE current set shares = :shares WHERE personid = :id',
                           shares=previous_shares + 1, id=session['user_id'])
                
                return redirect('/')
            
            except:
                is_in_db = db.execute('SELECT shares FROM current WHERE personid = :id AND stock = :stock', id = session['user_id'], stock = aDict["symbol"])
                
                if len(is_in_db) != 1:
                    #add user into db AND update stock AND return
                    db.execute('INSERT INTO current (personid, stock, shares, price) VALUES (:id, :stock, :shares, :price)',  id=session['user_id'], stock=aDict["symbol"], shares=request.form.get('shares'), price=price)
                    
                    return redirect('/')
                else:
                    # insert only stock into db
                    db.execute('INSERT INTO current (stock, shares, price) VALUES (:stock, :shares, :price) WHERE personid = :id', stock = aDict["symbol"], shares = request.form.get('shares'), price = price, id = session['user_id'])
                    
                    return redirect('/')
        
    if request.method == "GET":
        return render_template("buy.html")












@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    aDict = db.execute(
        'SELECT stock, shares, price, time FROM history WHERE personid = :id', id = session['user_id'])
    for i in range(len(aDict)):
        aDict[i]['price'] = usd(aDict[i]["price"], True)
    
    return render_template('history.html', aDict = aDict)










@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", msg="Must enter a username!")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", msg="Must enter a password!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", msg="Invalid username or password!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")










@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")









@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        
        if lookup(request.form.get("sym")) == None:
            
            return render_template('quote.html', msg = 'Invalid Stock')
        
        aDict = lookup(request.form.get("sym"))
        
        text = "A share of " + aDict["name"] + " (" + aDict["symbol"] + ") costs " + str(usd(aDict["price"])) + "."
        
        return render_template("quoted.html", msg = text)
        
    else:
        return render_template("quote.html")
    











@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("ruser"):

            return render_template("register.html", msg="Must enter a username!")
        
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("ruser"))
        
        if len(rows) > 0:
            
            return render_template("register.html", msg = 'Username Taken!')
        
        if not request.form.get("rpass"):
        
            return render_template("register.html", msg="Must enter a password!")
        
        if len(request.form.get('rpass')) < 8:
            
            return render_template("register.html", msg="Password must be at least 8 characters long and include a number!")

        if not hasNumbers(request.form.get('rpass')):
            
            return render_template("register.html", msg="Password must include a number!")
        
        
        if request.form.get("rpass") != request.form.get("rapass"):
        
            return render_template("register.html", msg="Passwords don't match!")
        
        db.execute("INSERT INTO users (username, hash) VALUES (:name, :hash)", name = request.form.get("ruser"), hash = generate_password_hash(request.form.get("rpass")))
        
        return redirect("/")
        
    else:
        return render_template("register.html")










@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    aDict = db.execute(
        'SELECT stock, shares, price FROM current WHERE personid = :id', id=session["user_id"])
    
    for i in range(len(aDict)):
        
        thing = lookup(aDict[i]["stock"])
        
        aDict[i]["name"] = thing["name"]
    
    if request.method == "POST":
    
        if not request.form.get('symbol'):
    
            return render_template("sell.html", msg="Please choose a stock", aDict=aDict)
    
        if not request.form.get('shares'):
    
            return render_template("sell.html", msg="Please enter the number of shares", aDict=aDict)
    
    
        thing = db.execute('SELECT shares FROM current WHERE personid = :id AND stock = :stock', id = session["user_id"], stock = request.form.get('symbol'))
    
        if float(thing[0]["shares"]) < float(request.form.get('shares')):
    
            return render_template("sell.html", msg="Too many shares", aDict=aDict)
    
        else:
    
            #Update history
    
            price = lookup(request.form.get('symbol'))

            price = 0 - (float(price["price"]) * float(request.form.get('shares')))
    
            db.execute('INSERT INTO history (personid, stock, shares, price) VALUES (:id, :symbol, :shares, :price)',
    
                       id=session["user_id"], symbol=request.form.get('symbol'), shares=0 - int(request.form.get('shares')), price=price)
    
        if float(thing[0]["shares"]) == float(request.form.get('shares')):
    
            #Completely delete share from current
    
            db.execute('DELETE FROM current WHERE personid = :id AND stock = :stock', id = session["user_id"], stock = request.form.get('symbol'))
    
        else:
    
            #Subtract the stock from current
    
            thing = db.execute('SELECT shares FROM current WHERE personid = :id AND stock = :stock', id = session["user_id"], stock = request.form.get('symbol'))
    
            thing = int(thing[0]["shares"])
    
            update = thing - float(request.form.get('shares'))
    
            db.execute('UPDATE current SET shares = :shares WHERE personid = :id AND stock = :stock', shares = update, id = session['user_id'], stock = request.form.get('symbol'))
    
        return redirect('/')
    
    else:
    
        return render_template("sell.html", aDict = aDict)













def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
