from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
import psycopg2
import os

API_KEY = "12345"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    quote = db.Column(db.String(500), unique=True, nullable=False)


db.create_all()


@app.route("/add-quote", methods=["GET", "POST"])
def add_quote():
    if request.args.get("api_key") == API_KEY:
        all_quotes = db.session.query(Quote).all()
        new_quote = Quote(number=len(all_quotes) + 1, quote=request.args.get("data"))
        db.session.add(new_quote)
        db.session.commit()
        return "Quote added."
    else:
        return jsonify(error={"Not Allowed": "Please provide a valid api key."})


@app.route("/del-quote", methods=["GET", "DELETE"])
def del_quote():
    if request.args.get("api_key") == API_KEY:
        quote_to_delete = Quote.query.filter_by(number=f'{request.args.get("data")}').first()
        if quote_to_delete:
            db.session.delete(quote_to_delete)
            all_quotes = Quote.query.order_by(Quote.number).all()
            for i in range(len(all_quotes)):
                all_quotes[i].number = i + 1
            db.session.commit()
            return "Quote deleted."
        else:
            return "Please use a valid quote number."
    else:
        return jsonify(error={"Not Allowed": "Please provide a valid api key."})


@app.route("/quote", methods=["GET"])
def get_quote():
    if request.args.get('data') == "list":
        return "http://api.litterbox.life/quote/list"
    elif request.args.get('data') == "":
        quote = Quote.query.order_by(func.random()).first()
        return quote.quote
    elif request.args.get('data').isnumeric():
        quote = Quote.query.filter_by(number=f"{request.args.get('data')}").first()
        if not quote:
            not_found = "Sorry, quote not found."
            return not_found
        else:
            return quote.quote
    else:
        quote = Quote.query.filter(Quote.quote.regexp_match(f"{request.args.get('data')}", '(?i)')).first()
        return quote.quote
        # if not lookup:
        #     not_found = "Sorry, quote not found."
        #     return not_found
        # else:
        #     quote = Quote.query.filter(Quote.quote.regexp_match(rf"\b(?i){request.args.get('data')}")).order_by(func.random()).first()
        #     return quote.quote


@app.route("/quote/list")
def quote_list():
    all_quotes = db.session.query(Quote).all()
    return render_template('list.html', all_quotes=all_quotes)


if __name__ == '__flask__':
    app.run(debug=True)
