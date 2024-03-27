import csv
from decimal import Decimal
import json
import re
from datetime import datetime, timedelta
import smtplib  # Import smtplib
import random
import string

import mysql.connector
import pandas as pd
from config import SECRET_KEY, MySQL_DB
from flask import Flask, Response, app, flash, g, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from api.user import user_bp

# Configure application
application = Flask(__name__)
application.secret_key = SECRET_KEY
# Register blueprints
application.register_blueprint(user_bp)



# Your SMTP server configuration
SMTP_SERVER = 'mail.informake.com'
SMTP_PORT = 465
SMTP_USERNAME = 'streasury@informake.com'
SMTP_PASSWORD = 'Moulana@1993'

# Configure email settings
application.config['MAIL_SERVER'] = SMTP_SERVER
application.config['MAIL_PORT'] = SMTP_PORT
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = SMTP_USERNAME
application.config['MAIL_PASSWORD'] = SMTP_PASSWORD

# Ensure templates are auto-reloaded
application.config["TEMPLATES_AUTO_RELOAD"] = True

    
# Ensure responses aren't cached
@application.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
application.jinja_env.filters["usd"] = usd

# Parameters for MySQL database
params = {
    "host": MySQL_DB.DB_HOST,
    "user": MySQL_DB.DB_USER,
    "passwd": MySQL_DB.DB_PASSWORD,
    "database": MySQL_DB.DB_NAME,
}


def open_database():
    """Opens a new database connection if there is none yet"""
    if not hasattr(g, "db"):
        g.db = mysql.connector.connect(**params)
        g.cursor = g.db.cursor(dictionary=True)
    return g.db, g.cursor


@application.teardown_appcontext
def close_database(error):
    """Closes the database connection at the end of the request"""
    if hasattr(g, "db"):
        g.db.close()

@application.route("/")
def home():
    """Shows Homepage"""

    return render_template("main.html")



@application.route("/check_credentials", methods=["GET", "POST"])
def check_credentials():
    """Log user in"""

    username = request.form.get("username")
    password = request.form.get("password")

    # Query the database to check if the credentials match
    db, cursor = open_database()
    cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, username))
    row = cursor.fetchone()

    if row and check_password_hash(row["hash_"], password):
        session["user_id"] = row["id"]
        session["user_email"] = row["email"]
        session["user_username"] = row["username"]
        session["virtual_credit"] = row["cash"]
        return jsonify({'success': True, 'redirect_url': '/market'})
    else:
        return jsonify({'success': False})
        
        
@application.route("/check_username", methods=["GET", "POST"])
def check_username():
    username = request.form.get("username")

    db, cursor = open_database()

    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        if existing_username:
            error_message = "Username is already in use"
            print("Error message:", error_message)  # Add this line for debugging
            return jsonify({"valid": False, "message": error_message})

        return jsonify({"valid": True, "message": "Valid input"})
    finally:
        cursor.close()  # Close the cursor in a finally block to ensure it's always closed

@application.route("/check_email", methods=["GET", "POST"])
def check_email():
    email = request.form.get("email")

    db, cursor = open_database()

    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            error_message = "Email is already in use"
            print("Error message:", error_message)  # Add this line for debugging
            return jsonify({"valid": False, "message": error_message})

        return jsonify({"valid": True, "message": "Valid input"})
    finally:
        cursor.close()  # Close the cursor in a finally block to ensure it's always closed


def generate_verification_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))


@application.route('/register', methods=['POST'])
def register():
    try:
        email = request.form.get("email")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        virtual_credit = 500000
        
        # Generate a verification token
        verification_token = generate_verification_token()
        token_expiration = datetime.now() + timedelta(days=1)  # Token expires in 1 day
        
        db, cursor = open_database()
        # Insert the user with verification information into the database
        cursor.execute(
            "INSERT INTO users (email, username, hash_, cash, verification_token, token_expiration) VALUES (%s, %s, %s, %s, %s, %s)",
            (email, username, password, virtual_credit, verification_token, token_expiration)
        )
        db.commit()
        new_user_id = cursor.lastrowid

        # Send a verification email
        # verification_link = url_for('verify_email', token=verification_token, _external=True)
        # msg = Message('Verify your email', recipients=[email])
        # msg.body = f'Click the following link to verify your email: {verification_link}'
        # mail.send(msg)
        
        
        cursor.execute('SELECT * FROM users WHERE id = %s', (new_user_id,))
        user_data = cursor.fetchone()

        session["user_id"] = user_data["id"]
        session["user_email"] = user_data["email"]
        session["user_username"] = user_data["username"]
        session["virtual_credit"] = user_data["cash"]
        session["registration"] = True

        flash('Registration successful. Check your email for a verification link.', 'success')
        return jsonify({"status": True, "message": "Successfully Registered"})
    except Exception as e:
        print(e)
        return jsonify({"status": False, "message": "Something Went Wrong"})
    
    
    
@application.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    cursor.execute("SELECT * FROM users WHERE verification_token = %s AND token_expiration > NOW()", (token,))
    user = cursor.fetchone()

    if user:
        # Mark the user as verified
        cursor.execute("UPDATE users SET is_verified = 1 WHERE verification_token = %s", (token,))
        db.commit()
        flash('Email verified. You can now log in.', 'success')
    else:
        flash('Invalid or expired verification link.', 'error')

    return redirect(url_for('login'))


# Create a function to send an email using SMTP
def send_email(subject, recipient, body):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = f'Subject: {subject}\n\n{body}'
        server.sendmail(SMTP_USERNAME, recipient, msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# Route to send a verification email (for testing)
@application.route("/sendemail", methods=["GET"])
def sendemail():
    verification_token = generate_verification_token()
    verification_link = url_for('verify_email', token=verification_token, _external=True)

    subject = 'Verify your email'
    recipient = 'karumpulihero@gmail.com'
    body = f'Click the following link to verify your email: {verification_link}'

    send_email(subject, recipient, body)

    return jsonify({"status": True, "message": "Verification email sent"})

# @application.route("/register", methods=["POST"])
# def register():
#     """Register user"""

#         # Add registered user into the database
#     try:
#             db, cursor = open_database()
#             cursor.execute(
#                 "INSERT INTO users (email,username, hash_, cash) VALUES (%s, %s, %s,%s)",
#                 (
#                     request.form.get("email"),
#                     request.form.get("username"),
#                     generate_password_hash(request.form.get("password")),
#                     500000
#                 ),
#             )
#             db.commit()
            
#             # Get the ID of the newly inserted user
#             new_user_id = cursor.lastrowid
#     except Exception as e:
#             print(e)
#             return jsonify({"status": False, "message": "Something Went Wrong"})

#         # Remember which user has registered
#     cursor.execute('SELECT * FROM users WHERE id = %s', (new_user_id,))
#     user_data = cursor.fetchone()

#     session["user_id"] = user_data["id"]
#     session["user_email"] = user_data["email"]
#     session["user_username"] = user_data["username"]
#     session["virtual_credit"] = user_data["cash"]
#     session["registration"] = True

#         # Redirect the user to the home page
#     return jsonify({"status": True, "message": "Successfully Registered"})



@application.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@application.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    """Allow users to reset password"""
    db, cursor = open_database()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username and keyword
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND keyword=%s",
            (request.form.get("username"), request.form.get("keyword")),
        )

        # Ensure username/keyword combination exists
        if not cursor.fetchone():
            return apology("Username/Keyword combination invalid")

        # Update user's new password
        cursor.execute(
            "UPDATE users SET hash_=%s WHERE username=%s",
            (
                generate_password_hash(request.form.get("new_password")),
                request.form.get("username"),
            ),
        )
        db.commit()

        # Redirect user to success landing page
        return redirect("/password-reset-success")

    else:
        return render_template("password-reset.html")


@application.route("/password-reset-success")
def reset_success():
    return render_template("password-reset-success.html")


@application.route("/portfolio", methods=["GET", "POST"])
@login_required
def portfolio():
    """Shows user's portfolio"""
    db, cursor = open_database()
    cursor.execute(
        "SELECT * FROM portfolio WHERE user_id=%s",
        (session["user_id"],),
    )
    user_stocks = cursor.fetchall()

    total_stock_value = 0

    # Get current prices and update portfolio
    for stock in user_stocks:
        stock_symbol = stock["symbol"]
        owned_shares = stock["shares"]
        stock_info = lookup(stock_symbol)
        market_price_per_share = float(stock_info["price"])
        total_market_price = owned_shares * market_price_per_share
        total_stock_value += total_market_price
        cursor.execute(
            "UPDATE portfolio SET price=%s, total=%s WHERE user_id=%s AND symbol=%s",
            (
                market_price_per_share,
                total_market_price,
                session["user_id"],
                stock_symbol,
            ),
        )
        db.commit()

    # If shares are equal to 0 then delete from portfolio
    cursor.execute("DELETE FROM portfolio WHERE user_id=%s AND shares=0", (session["user_id"],))
    db.commit()

    # Get user's available cash
    cursor.execute("SELECT cash FROM users WHERE id=%s", (session["user_id"],))
    available_cash = cursor.fetchone()

    # Add user's available cash to total holdings
    total_portfolio_value = available_cash["cash"] + Decimal(total_stock_value)

    # Get current portfolio
    cursor.execute("SELECT * FROM portfolio WHERE user_id=%s ORDER BY symbol", (session["user_id"],))
    current_portfolio = cursor.fetchall()

    return render_template(
        "portfolio.html",
        stocks=current_portfolio,
        user_cash=usd(available_cash["cash"]),
        grand_total=usd(total_portfolio_value),
    )


@application.route("/market")
@login_required
def market():
    
    if 'registration' in session:
        session.pop('registration', None)  # Remove the 'registration' session variable
        return render_template("market.html")
    else:
        return render_template("market.html")
    

@application.route("/innovative_solution")
def innovative_solution():
    return render_template("innovative.html")


@application.route("/marketwatch")
# @login_required
def marketwatch():
    symbol = request.args.get('symbol')
    return render_template("market_watch_api.html", symbol=symbol)
    

@application.route('/history', methods=['GET'])
def history():
    # time, open, high, low, close, volume, symbol
    symbol = request.args.get('symbol')
    resolution = request.args.get('resolution')
    from_timestamp = int(request.args.get('from')) * 1000  # Convert to milliseconds
    to_timestamp = int(request.args.get('to')) * 1000      # Convert to milliseconds
    
    # Retrieve data from the database based on the symbol and timestamp range
    db, cursor = open_database()
    query = f"SELECT * FROM transaction_history WHERE symbol = '{symbol}' AND time >= {from_timestamp} AND time <= {to_timestamp}"
    cursor.execute(query)
    db_data = cursor.fetchall()

    # Format the retrieved data
    historical_data = []
    for row in db_data:
        data_point = {
            "timestamp": int(row['time']), 
            "open": row['open'],
            "high": row['high'],
            "low": row['low'],
            "close": row['close'],
            "volume": row['volume']
        }
        historical_data.append(data_point)

    # Adjust the data based on the resolution
    # For simplicity, we're returning the same data as is
    # In a real implementation, you'd aggregate data based on the resolution

    response = {
        "s": "ok",
        "t": [data['timestamp'] //1000 for data in historical_data],  # Convert back to seconds
        "o": [data['open'] for data in historical_data],
        "h": [data['high'] for data in historical_data],
        "l": [data['low'] for data in historical_data],
        "c": [data['close'] for data in historical_data],
        "v": [data['volume'] for data in historical_data]
    }

    return jsonify(response)


@application.route('/latest_data', methods=['GET'])
def latest_data():
    # Retrieve the latest record for each symbol
    db, cursor = open_database()
    query = """
WITH LatestTransaction AS (
    SELECT
        c.name,
        c.symbol,
        c.logo,
        c.industry,
        th.time AS latest_time,
        th.open,
        th.high,
        th.low,
        th.close,
        th.volume,
        LAG(th.close) OVER (PARTITION BY c.symbol ORDER BY th.time) AS prev_close,
        ROW_NUMBER() OVER (PARTITION BY c.symbol ORDER BY th.time DESC) AS rn
    FROM
        companies c
    INNER JOIN
        transaction_history th ON c.symbol = th.symbol
)
SELECT
    name,
    symbol,
    industry,
    logo,
    latest_time,
    open,
    high,
    low,
    close,
    volume,
    ROUND((close - COALESCE(prev_close, 0)), 2) AS close_price_change,
    ROUND(
        CASE
            WHEN prev_close IS NOT NULL AND prev_close <> 0 THEN
                ((close - prev_close) / prev_close) * 100
            ELSE
                0
        END, 2
    ) AS close_price_change_percentage
FROM
    LatestTransaction
WHERE
    rn = 1;

    """
    cursor.execute(query)
    db_data = cursor.fetchall()

    # Format the retrieved data
    latest_data = []
    for row in db_data:
        data_point = row
        latest_data.append(data_point)

    response = {
        "s": "ok",
        "latest_data": latest_data
    }

    return jsonify(response)



@application.route('/symbol_profile', methods=['GET'])
def symbol_profile():
    try:
        symbol = request.args.get('symbol')

        db, cursor = open_database()
        query = "SELECT * FROM companies"
        cursor.execute(query)
        data = cursor.fetchone()

        if data:

            return jsonify({"status": "success", "data": data})
        else:
            return jsonify({"status": "error", "message": "Symbol not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


@application.route('/get_user', methods=['POST'])
def get_user():
    try:
        data = request.get_json()
        email = data.get('email')

        db, cursor = open_database()
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (email, email))
        user_data = cursor.fetchone()

        if user_data:
            return jsonify({"status": "success", "data": user_data}),200
        else:
            return jsonify({"status": "error email", "message": email}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
            
            
            
@application.route('/config', methods=['GET'])
def config():
    response = {
        "supports_search": True,
        "supports_group_request": False,
        "supports_marks": False,
        "supports_timescale_marks": False,
        "supports_time": True
    }

    return jsonify(response)

@application.route('/time', methods=['GET'])
def get_time():
    # You can customize the response format if needed
    response = {
        "server_time": "2023-08-19 12:00:00"
    }
    return jsonify(response)


@application.route('/symbols', methods=['GET'])
def get_symbols():
    symbol = request.args.get('symbol')
    
    
    db, cursor = open_database()

            # Execute the SQL query to retrieve company information
    query = "SELECT * FROM companies WHERE symbol = %s"
    cursor.execute(query, (symbol,))
    company = cursor.fetchone()
    # Sample response for demonstration purposes
    response = {
        company['symbol']: {
             "exchange": "QSE",
             "type": "stock",
             "listed_exchange": "QSE",
             "timezone": "UTC+3",
             "minmov": 1,
             "pricescale": 100,
             "session": "0930-1330,1415-1530",
             "closed_days": ["Fr", "Sat"],
             "has_intraday": True,
             "has_no_volume": False,
             "country": "Qatar",
             "currency": "QAR",
             "name": company['symbol'],
             "sector": company['industry'],
             "industry": company['industry'],
             "description": company['name']
        },
        
        # Add more symbols as needed
    }
    
    if symbol in response:
        return jsonify(response[symbol])
    else:
        return jsonify({"error": "Symbol not found"}), 404


##############Graph End############


##############API Start ############

@application.route('/register_user', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if username, email, and password are provided
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 422

    # Validate email format
    if not re.match(r'^\S+@\S+\.\S+$', email):
        return jsonify({'error': 'Invalid email format'}), 422

    # Validate username and password criteria (e.g., minimum length)
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 422
    # Validate username and password criteria (e.g., minimum length)
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 422

    db, cursor = open_database()

    try:
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            if existing_user['username'] == username:
                return jsonify({'error': 'Username already exists'}), 422
            else:
                return jsonify({'error': 'Email already exists'}), 422

        
        hashed_password = generate_password_hash(password)
        cash_amount = 500000
        cursor.execute('INSERT INTO users (username, email, hash_, cash) VALUES (%s, %s, %s, %s)', (username, email, hashed_password, cash_amount))
        db.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'error': 'An error occurred while registering.'}), 500
    finally:
        db.close()
        
        
    #     if existing_user:
    #         if existing_user[0] == username:
    #             return jsonify({'error': 'Username already exists'}), 422
    #         else:
    #             return jsonify({'error': 'Email already exists'}), 422

    #     # Insert the new user into the database
    #     hashed_password = generate_password_hash(password)
    #     cash_amount = 500000
    #     cursor.execute('INSERT INTO users (username, email, hash_, cash) VALUES (%s, %s, %s, %s)', (username, email, hashed_password, cash_amount))
    #     db.commit()

    #     return jsonify({'message': 'Registration successful'}), 201
    # except Exception as e:
    #     db.rollback()  # Rollback the transaction to avoid partial data insertion
    #     print(str(e))  # Print the exception message for debugging
    #     return jsonify({'error': 'An error occurred while registering'}), 500

    # finally:
    #     db.close()


@application.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    db, cursor = open_database()

    try:
        # Check if the username or email matches
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, username))
        user_data = cursor.fetchone()
        
        if user_data and check_password_hash(user_data["hash_"], password):  # Assuming password_hash is in the third column
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': 'An error occurred while logging in'}), 500
    finally:
        db.close()

        

@application.route('/record_preferred', methods=['POST'])
def record_preferred():
    try:
        data = request.get_json()
        user_id = data['user_id']
        symbol = data['symbol']

        # Check if the user and symbol combination already exists in the database
        db, cursor = open_database()

        cursor.execute(
            "SELECT * FROM preferred WHERE user_id = %s AND symbol = %s",
            (user_id, symbol)
        )

        existing_record = cursor.fetchone()

        if existing_record:
            # The record already exists, so you can handle this case as needed
            db.close()
            return jsonify({'message': 'Record already exists'}), 200
        else:
            # Insert the preferred into the MySQL database
            cursor.execute(
                "INSERT INTO preferred (user_id, symbol) VALUES (%s, %s)",
                (user_id, symbol)
            )
            db.commit()
            db.close()
            return jsonify({'message': 'Record inserted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@application.route('/get_preferred', methods=['GET'])
def get_preferred():
    try:
        user_id = request.args.get('user_id')
        
        # Fetch orders from the MySQL database based on filters
        db, cursor = open_database()

        cursor.execute("SELECT * FROM preferred WHERE user_id=%s ORDER BY preferred_id DESC",(user_id,))

        preferred = cursor.fetchall()
        db.close()

        return jsonify({'preferred': preferred}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@application.route('/get_preferred_details', methods=['GET'])
def get_preferred_details():
    user_id = request.args.get('user_id')
    # Retrieve the latest record for each symbol
    db, cursor = open_database()
    query = f"""
WITH LatestTransaction AS (
    SELECT
        c.name,
        c.symbol,
        c.logo,
        c.industry,
        th.time AS latest_time,
        th.open,
        th.high,
        th.low,
        th.close,
        th.volume,
        LAG(th.close) OVER (PARTITION BY c.symbol ORDER BY th.time) AS prev_close,
        ROW_NUMBER() OVER (PARTITION BY c.symbol ORDER BY th.time DESC) AS rn
    FROM
        companies c
    INNER JOIN
        transaction_history th ON c.symbol = th.symbol
    INNER JOIN
        preferred p ON c.symbol = p.symbol  -- Inner join with 'preferred' table
    WHERE
        p.user_id = {user_id}  -- Filter by user_id
)
SELECT
    name,
    symbol,
    industry,
    logo,
    latest_time,
    open,
    high,
    low,
    close,
    volume,
    ROUND((close - COALESCE(prev_close, 0)), 2) AS close_price_change,
    ROUND(
        CASE
            WHEN prev_close IS NOT NULL AND prev_close <> 0 THEN
                ((close - prev_close) / prev_close) * 100
            ELSE
                0
        END, 2
    ) AS close_price_change_percentage
FROM
    LatestTransaction
WHERE
    rn = 1;
    """
    cursor.execute(query)
    db_data = cursor.fetchall()

    # Format the retrieved data
    preferred = []
    for row in db_data:
        data_point = row
        preferred.append(data_point)

    response = {
        "s": "ok",
        "preferred": preferred
    }

    return jsonify(response)

    

@application.route('/delete_preferred', methods=['POST'])
def delete_preferred():
    try:
        data = request.get_json()
        user_id = data['user_id']
        symbol = data['symbol']

        # Delete the preferred item from the MySQL database
        db, cursor = open_database()

        cursor.execute("DELETE FROM preferred WHERE user_id = %s AND symbol = %s", (user_id, symbol))

        db.commit()
        db.close()

        return jsonify({'message': 'Preferred item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        

@application.route('/get_orders', methods=['GET'])
def get_orders():
    try:
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        # Fetch orders from the MySQL database based on filters
        db, cursor = open_database()

        if status =='pending':
            cursor.execute(
                "SELECT * FROM orders INNER JOIN companies ON orders.symbol=companies.symbol WHERE user_id=%s AND order_status=%s ORDER BY order_id DESC",
                (user_id, status)
            )
        else:
            cursor.execute(
                "SELECT * FROM orders INNER JOIN companies ON orders.symbol=companies.symbol WHERE user_id=%s AND order_status<>%s ORDER BY order_id DESC",
                (user_id, 'pending')
            ) 
       

        orders = cursor.fetchall()
        db.close()

        return jsonify({'orders': orders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        

@application.route('/place_order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()

        user_id = data['user_id']
        symbol = data['symbol']
        order_type = data['order_type']
        order_price = data['order_price']
        order_quantity = data['order_quantity']

        # Insert the order into the MySQL database
        db, cursor = open_database()
        cursor.execute(
            "INSERT INTO orders (user_id, symbol, order_type, order_price, order_quantity, order_status) "
            "VALUES (%s, %s, %s, %s, %s, 'pending')",
            (user_id, symbol, order_type, order_price, order_quantity)
        )
        db.commit()
        db.close()

        return jsonify({'message': 'Order placed successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@application.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        # Connect to the database
        db, cursor = open_database()


        # Delete the order with the given order_id
        delete_query = "DELETE FROM orders WHERE order_id = %s"
        cursor.execute(delete_query, (order_id,))
        db.commit()

        cursor.close()
        db.close()

        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error deleting order: {str(e)}'}), 500




@application.route('/get_companies', methods=['GET'])
def get_companies():
    try:
        
        # Fetch companies from the MySQL database based on filters
        db, cursor = open_database()

        cursor.execute("SELECT * FROM companies")
       
        companies = cursor.fetchall()
        db.close()

        return jsonify({'companies': companies}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@application.route('/get_holding_stocks', methods=['GET'])
def get_holding_stocks():
    try:
        user_id = request.args.get('user_id')
        # Fetch orders from the MySQL database based on filters
        db, cursor = open_database()

       
        cursor.execute("""
    SELECT
        *,
        SUM(orders.order_quantity) AS shares_count,
        FORMAT(AVG(orders.order_price), 2) AS buy_average,
        FORMAT(th.close, 2) AS recent_close_price,
        FORMAT(SUM(orders.order_quantity) * th.close, 2) AS market_value,
        FORMAT((SUM(orders.order_quantity) * th.close) - (SUM(orders.order_quantity) * FORMAT(AVG(orders.order_price), 2)), 2) AS profit_loss,
        FORMAT(((SUM(orders.order_quantity) * th.close) - (SUM(orders.order_quantity) * FORMAT(AVG(orders.order_price), 2))) / (SUM(orders.order_quantity) * FORMAT(AVG(orders.order_price), 2)) * 100, 2) AS profit_percentage

    FROM
        orders
    INNER JOIN
        companies ON orders.symbol = companies.symbol
    LEFT JOIN (
        SELECT
            symbol,
            MAX(time) AS recent_time,
            close
        FROM
            transaction_history
        GROUP BY
            symbol
    ) AS th ON orders.symbol = th.symbol
    WHERE
        user_id = %s
        AND order_type = 'buy'
        AND order_status = 'completed'
    GROUP BY
        orders.symbol
""", (user_id,))
 
        stocks = cursor.fetchall()

        
        cursor.execute("""
    SELECT
        -- Calculate total value
        total_value.total_value,
        
        -- Calculate equity
         FORMAT((total_value.total_value - COALESCE(debt.debt, 0)),2) AS equity,
        
        -- Calculate debt
        FORMAT(COALESCE(debt.debt, 0),2) AS debt
    FROM (
        -- Calculate total value of the portfolio
        SELECT
            SUM(shares_count * recent_close_price) AS total_value
        FROM (
            SELECT
                SUM(orders.order_quantity) AS shares_count,
                th.close AS recent_close_price
            FROM
                orders
            INNER JOIN
                companies ON orders.symbol = companies.symbol
            LEFT JOIN (
                SELECT
                    symbol,
                    MAX(time) AS recent_time,
                    close
                FROM
                    transaction_history
                GROUP BY
                    symbol
            ) AS th ON orders.symbol = th.symbol
            WHERE
                user_id = %s
                AND order_type = 'buy'
                AND order_status = 'completed'
            GROUP BY
                orders.symbol
        ) AS portfolio
    ) AS total_value
    LEFT JOIN (
        -- Calculate debt
        SELECT
            SUM(order_quantity * order_price) AS debt
        FROM
            orders
        WHERE
            user_id = %s
            AND order_type = 'sell'
            AND order_status = 'completed'
    ) AS debt ON 1 = 1
""", (user_id, user_id,))
        summary = cursor.fetchall()
        db.close()


        return jsonify({'stocks': stocks},{'summary': summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@application.route('/overall_market_data', methods=['GET'])
def overall_market_data():
    try:
        db, cursor = open_database()

        # Get the latest time with available data
        cursor.execute("SELECT MAX(time) as timestamp FROM transaction_history;")
        row = cursor.fetchone()
        latest_timestamp = row["timestamp"]

        if latest_timestamp is None:
            return jsonify({"error": "No data available"})

        # Calculate the total index value and total volume for the latest time
        cursor.execute("SELECT SUM(close) as index_value FROM transaction_history WHERE time = %s;", (latest_timestamp,))
        row = cursor.fetchone()
        total_index_value = row["index_value"]

        cursor.execute("SELECT SUM(volume) as total_volume FROM transaction_history WHERE time = %s;", (latest_timestamp,))
        row = cursor.fetchone()
        total_volume = row["total_volume"]

        # Calculate Percentage Change (You need a previous reference value for this)
        # You can retrieve the previous reference value from your database as well
        cursor.execute("SELECT close FROM transaction_history WHERE time = (SELECT MAX(time) FROM transaction_history WHERE time < %s);", (latest_timestamp,))
        row = cursor.fetchone()
        
        if row:
            previous_index_value = row["close"]
        else:
            previous_index_value = 0

        if previous_index_value == 0:
            percentage_change = 0  # Set percentage change to 0 if previous_index_value is 0
        else:
            # Check if the values are strings and convert them to floats if needed
            if isinstance(total_index_value, str):
                total_index_value = float(total_index_value)
            if isinstance(previous_index_value, str):
                previous_index_value = float(previous_index_value)
            percentage_change = ((total_index_value - previous_index_value) / previous_index_value) * 100

        # Prepare the response
        response = {
            "index_value": round(total_index_value, 2),
            "percentage_change": round(percentage_change, 2),
            "total_volume": total_volume
        }

        return jsonify({'data': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


##############API End ############


################Core #############


@application.route('/execute_trades', methods=['GET'])
def execute_trades():
    
    db, cursor = open_database()
    # Fetch all pending sell orders from the orders table
    cursor.execute("SELECT * FROM orders WHERE order_type = 'sell' AND order_status = 'pending'")
    sell_orders = cursor.fetchall()
    timestamp=0
    for sell_order in sell_orders:
        symbol = sell_order['symbol']
        sell_price = sell_order['order_price']

        # Convert datetime object to a Unix timestamp (milliseconds since epoch)
        timestamp = int(sell_order['order_date'].timestamp() * 1000)
        timestamp += 1000  # Increase by 1 second
        # Create a record in the transaction history table
        cursor.execute("INSERT INTO transaction_history (time,open, low, high, close, volume, symbol, resolution) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)",
                       (timestamp,sell_price, sell_price, sell_price, sell_price, sell_order['order_quantity'], symbol, '1D'))
        db.commit()
        
        # Mark the buy orders as partial
        cursor.execute("UPDATE orders SET order_status = 'partial' WHERE order_id = %s", (sell_order['order_id'],))
        db.commit()

        # Fetch matching pending buy orders for the same symbol
        cursor.execute("SELECT * FROM orders WHERE order_type = 'buy' AND order_status = 'pending' AND symbol = %s", (symbol,))
        buy_orders = cursor.fetchall()
        
        for buy_order in buy_orders:
            buy_price = buy_order['order_price']

            # Check if the buy price is equal or higher than the open selling price
            if buy_price >= sell_price:
                # Update the transaction record with low, high, and volume prices
                cursor.execute("UPDATE transaction_history SET low = %s, high = %s, volume = %s, resolution = %s, close = %s WHERE time = %s",
                              (buy_price, buy_price, buy_order['order_quantity'],'1D',buy_price, timestamp))
                db.commit()
               
                # Mark the buy and sell orders as executed
                cursor.execute("UPDATE orders SET order_status = 'completed' WHERE order_id = %s", (sell_order['order_id'],))
                cursor.execute("UPDATE orders SET order_status = 'completed' WHERE order_id = %s", (buy_order['order_id'],))
                db.commit()

    return jsonify({"message": "Trades executed successfully"}), 200


################Core End #########


@application.route("/page_not_found")
def page_404():
    """Shows 404 page"""

    return render_template("404.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    application.errorhandler(code)(errorhandler)

# Serve the HTML file from the 'static' directory
@application.route('/<path:path>', methods=['GET'])
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    # application.run()
    application.run(debug=True)
