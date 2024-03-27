import json
import urllib.parse
from functools import wraps
import requests
from flask import Response, redirect, render_template, session


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    return render_template("404.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function



def lookup(symbol):
    return read_stock_data(symbol)



def read_stock_data(symbol):
    try:
        with open('stocks.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['symbol'] == symbol:
                    return {
                        "name": row["companyName"],
                        "price": float(row["latestPrice"]),
                        "symbol": row["symbol"],
                        "logo": f"/static/assets/companies/{row['symbol']}.jpg",  # Use f-string for formatting
                    }
    except FileNotFoundError:
        return None

    return None

def usd(value):
    """Format value as QAR."""
    return f"QAR{value:,.2f}"
