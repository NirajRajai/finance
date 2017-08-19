from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    details_hist=db.execute("SELECT symbol,share,price,pricea FROM histories WHERE id=:id ",id=session["user_id"])
    if not details_hist:
        return apology("Nothing to display")
    details_user=db.execute("SELECT username,cash from users WHERE id=:id ",id=session["user_id"])
    if not details_user:
        return apology("nothing to display")
    return apology("TODO")
    

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        data=lookup(request.form.get("Stock"))
        if not data:
            return apology("Invalid Symbol")
        if not request.form.get("number"):
            return apology("must provide number of shares")
        try:
            shares = int(request.form.get("number"))
            if shares < 0:
                return apology("Shares must be positive integer")
        except:
                return apology("Shares must be positive integer")
        availaible=db.execute("SELECT cash FROM users WHERE id=:id",id=session["user_id"])
        if float(availaible[0]["cash"]) < data["price"] * shares:
                        return apology("Not enough money")
        exist=db.execute("INSERT INTO histories VALUES(:symbol,:share,:price,:id,:pricea)",symbol=request.form.get("Stock"),share=shares,price=usd(data["price"]),id=session["user_id"],pricea=float(data["price"]))
        if not exist:
            db.execute("UPDATE histories SET share=share + :share WHERE id=:id AND symbol=:symbol",share=shares,id=session["user_id"],symbol=request.form.get("Stock"))
        db.execute("UPDATE users SET cash = cash - :purchase WHERE id = :id",purchase=int(data["price"]) * shares,id=session["user_id"])
        return render_template("index.html")
    else:
        return render_template("buy.html")
    
@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        data=lookup(request.form.get("Stock"))
        if not data:
            return apology("Invalid Symbol")
        return render_template("quoted.html",stock=data)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif request.form.get("password")!=request.form.get("confirm_password"):
            return apology("passwords do not match")
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",username=request.form.get("username"), hash= pwd_context.hash(request.form.get("password")))
                 
        if not result:
            return apology("Username already exist")
        
        # remember which user has logged in
        session["user_id"] = result

        # redirect user to home page
        return redirect(url_for("index"))
    
    else:
        return render_template("register.html")                

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    return apology("TODO")
