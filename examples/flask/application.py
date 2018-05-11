import os
import re
from flask import Flask, jsonify, render_template, request

from cs50 import SQL
from helpers import lookup

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mashup.db")


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Render map"""
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")
    return render_template("index.html", key=os.environ.get("API_KEY"))


@app.route("/articles")
def articles():
    """Look up articles for geo"""
    geo = request.args.get("geo")
    if not geo:
        raise RuntimeError("missing geo")
    data = lookup(geo)
    if len(data) <= 5:
        return jsonify(data)
    else:
        return jsonify(data[:5])


@app.route("/search")
def search():
    """Search for places that match query"""
    rows = []
    q = request.args.get("q")
    if not q:
        raise RuntimeError("missing q")

    '''
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS vt USING fts4(content='places', postal_code, place_name, admin_name1, admin_code1)")
    db.execute("INSERT INTO vt(vt) VALUES('rebuild')")
    rows = db.execute("SELECT * FROM vt WHERE postal_code MATCH :q0", q0=listq[0])
    '''
    if ',' in q:
        listq = [x.strip() for x in q.split(',')]
    else:
        listq = [x.strip() for x in q.split(' ')]
    Listqlen = len(listq)
    # print("listq = " + str(listq))
    # print("len(listq) = " + str(len(listq)))

    if Listqlen == 1:
        if listq[0].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE place_name LIKE (:q0)
                              OR postal_code LIKE (:q1)
                              OR latitude LIKE (:q0)
                              OR longitude LIKE (:q0)
                              OR country_code LIKE (:q0)""", q0="%" + listq[0] + "%", q1=listq[0] + "%")
        else:
            rows = db.execute("""SELECT * FROM places WHERE place_name LIKE (:q0)
                              OR country_code LIKE (:q0)""", q0="%" + listq[0] + "%")
    elif Listqlen == 2:
        if listq[0].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE place_name = :q0
                              OR postal_code = :q0
                              OR latitude = :q0
                              OR longitude = :q0
                              OR country_code = :q0
                              AND (place_name = :q1
                              OR country_code = :q1
                              OR admin_code1 = :q1
                              OR admin_code2 = :q1
                              OR admin_code3 = :q1
                              OR admin_name1 = :q1
                              OR admin_name2 = :q1
                              OR admin_name3 = :q1)""", q0=listq[0], q1=listq[1])
        elif listq[1].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE place_name = :q0
                              OR postal_code = :q0
                              OR latitude = :q0
                              OR longitude = :q0
                              OR country_code = :q0
                              AND (place_name = :q1
                              OR country_code = :q1
                              OR admin_code1 = :q1
                              OR admin_code2 = :q1
                              OR admin_code3 = :q1
                              OR admin_name1 = :q1
                              OR admin_name2 = :q1
                              OR admin_name3 = :q1)""", q0=listq[1], q1=listq[0])
        else:
            rows = db.execute("""SELECT * FROM places WHERE (place_name LIKE :q0
                              OR country_code LIKE :q0
                              OR admin_code1 LIKE :q0
                              OR admin_code2 LIKE :q0
                              OR admin_code3 LIKE :q0
                              OR admin_name1 LIKE :q0
                              OR admin_name2 LIKE :q0
                              OR admin_name3 LIKE :q0)
                              AND (place_name LIKE :q1
                              OR country_code LIKE :q1
                              OR admin_code1 LIKE :q1
                              OR admin_code2 LIKE :q1
                              OR admin_code3 LIKE :q1
                              OR admin_name1 LIKE :q1
                              OR admin_name2 LIKE :q1
                              OR admin_name3 LIKE :q1)""", q0=listq[0] + '%', q1='%' + listq[1] + '%')
    elif Listqlen == 3:
        if listq[0].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE
                              (place_name LIKE :q0
                              OR postal_code LIKE :q0_1
                              OR latitude LIKE :q0
                              OR longitude LIKE :q0
                              OR country_code LIKE :q0)
                              AND (country_code LIKE :q1
                              OR place_name LIKE :q1
                              OR admin_code1 LIKE :q1
                              OR admin_code2 LIKE :q1
                              OR admin_code3 LIKE :q1
                              OR admin_name1 LIKE :q1
                              OR admin_name2 LIKE :q1
                              OR admin_name3 LIKE :q1)
                              AND (place_name LIKE :q2
                              OR country_code LIKE :q2
                              OR admin_code1 LIKE :q2
                              OR admin_code2 LIKE :q2
                              OR admin_code3 LIKE :q2
                              OR admin_name1 LIKE :q2
                              OR admin_name2 LIKE :q2
                              OR admin_name3 LIKE :q2)""", q0="%" + listq[0] + "%", q0_1=listq[0] + "%", q1='%' + listq[1] + '%', q2='%' + listq[2] + '%')
        elif listq[1].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE
                              (place_name LIKE :q0
                              OR postal_code LIKE :q0_1
                              OR latitude LIKE :q0
                              OR longitude LIKE :q0
                              OR country_code LIKE :q0)
                              AND (country_code LIKE :q1
                              OR place_name LIKE :q1
                              OR admin_code1 LIKE :q1
                              OR admin_code2 LIKE :q1
                              OR admin_code3 LIKE :q1
                              OR admin_name1 LIKE :q1
                              OR admin_name2 LIKE :q1
                              OR admin_name3 LIKE :q1)
                              AND (place_name LIKE :q2
                              OR country_code LIKE :q2
                              OR admin_code1 LIKE :q2
                              OR admin_code2 LIKE :q2
                              OR admin_code3 LIKE :q2
                              OR admin_name1 LIKE :q2
                              OR admin_name2 LIKE :q2
                              OR admin_name3 LIKE :q2)""", q0="%" + listq[1] + "%", q0_1=listq[1] + "%", q1='%' + listq[0] + '%', q2='%' + listq[2] + '%')
        elif listq[2].isdigit():
            rows = db.execute("""SELECT * FROM places WHERE
                              (place_name LIKE :q0
                              OR postal_code LIKE :q0_1
                              OR latitude LIKE :q0
                              OR longitude LIKE :q0
                              OR country_code LIKE :q0)
                              AND (country_code LIKE :q1
                              OR place_name LIKE :q1
                              OR admin_code1 LIKE :q1
                              OR admin_code2 LIKE :q1
                              OR admin_code3 LIKE :q1
                              OR admin_name1 LIKE :q1
                              OR admin_name2 LIKE :q1
                              OR admin_name3 LIKE :q1)
                              AND (place_name LIKE :q2
                              OR country_code LIKE :q2
                              OR admin_code1 LIKE :q2
                              OR admin_code2 LIKE :q2
                              OR admin_code3 LIKE :q2
                              OR admin_name1 LIKE :q2
                              OR admin_name2 LIKE :q2
                              OR admin_name3 LIKE :q2)""", q0="%" + listq[2] + "%", q0_1=listq[2] + "%", q1='%' + listq[1] + '%', q2='%' + listq[0] + '%')
        else:
            rows = db.execute("""SELECT * FROM places WHERE
                              (place_name LIKE :q0
                              OR admin_code1 LIKE :q0
                              OR admin_code2 LIKE :q0
                              OR admin_code3 LIKE :q0
                              OR admin_name1 LIKE :q0
                              OR admin_name2 LIKE :q0
                              OR admin_name3 LIKE :q0
                              OR country_code LIKE :q0)
                              AND (country_code LIKE :q1
                              OR place_name LIKE :q1
                              OR admin_code1 LIKE :q1
                              OR admin_code2 LIKE :q1
                              OR admin_code3 LIKE :q1
                              OR admin_name1 LIKE :q1
                              OR admin_name2 LIKE :q1
                              OR admin_name3 LIKE :q1)
                              AND (place_name LIKE :q2
                              OR country_code LIKE :q2
                              OR admin_code1 LIKE :q2
                              OR admin_code2 LIKE :q2
                              OR admin_code3 LIKE :q2
                              OR admin_name1 LIKE :q2
                              OR admin_name2 LIKE :q2
                              OR admin_name3 LIKE :q2)""", q0="%" + listq[0] + "%", q1='%' + listq[1] + '%', q2='%' + listq[2] + '%')

    '''
        #q0 = listq[0] + "%"
        rows = db.execute("""SELECT * FROM vt WHERE place_name MATCH (:q0)
                          OR postal_code like (:q0)
                          OR country_code like (:q0)""", q0=q0)
    elif len(listq) == 2:
        listq.append("")
        listq.append("")

    rows = db.execute("""SELECT * FROM places WHERE place_name IN (:q0 , :q1, :q2)
                       AND country_code IN (:q0 , :q1, :q2)
                       AND postal_code IN (:q0 , :q1, :q2)
                       LIMIT 10""",
                       q0=listq[0], q1=listq[1], q2=listq[2])
    '''

    #rows = db.execute("SELECT * FROM places WHERE place_name IN (:q2)", q2=listq[0])

    return jsonify(rows)


@app.route("/update")
def update():
    """Find up to 10 places within view"""

    # Ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # Ensure parameters are in lat,lng format
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # Explode southwest corner into two variables
    sw_lat, sw_lng = map(float, request.args.get("sw").split(","))

    # Explode northeast corner into two variables
    ne_lat, ne_lng = map(float, request.args.get("ne").split(","))

    # Find 10 cities within view, pseudorandomly chosen if more within view
    if sw_lng <= ne_lng:

        # Doesn't cross the antimeridian
        # use AND in second line
        rows = db.execute("""SELECT * FROM places
                          WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude AND longitude <= :ne_lng)
                          GROUP BY country_code, place_name, admin_code1
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # Crosses the antimeridian
        # use OR in second line
        rows = db.execute("""SELECT * FROM places
                          WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude OR longitude <= :ne_lng)
                          GROUP BY country_code, place_name, admin_code1
                          ORDER BY RANDOM()
                          LIMIT 10""",
                          sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    '''
    print()
    print()
    print()
    print("jsonify[rows] = " + str(rows))
    print()
    print()
    print()
    print("rows[0][latitude] = " + str(rows[0]["latitude"]))
    print("rows[0][longitude] = " + str(rows[0]["longitude"]))
    print("rows = " + str(len(rows)))
    '''

    # Output places as JSON
    return jsonify(rows)
