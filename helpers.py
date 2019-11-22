import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def naira(value):
    """Format value as Naira."""
    return f"{value:,.2f}"

# Function to send mails
def send_mail(to, subject, message):
    message = Mail(
        from_email='info@decacredit.com.ng',
        to_emails=to,
        subject=subject,
        html_content=message or '<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
    #pass