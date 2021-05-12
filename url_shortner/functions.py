import string
from random import choices

import re


def validated_shortcode_insert(db, url, shortcode):
    """ Validates the entered shortcode and inserts into db if valid"""
    if not shortcode:
        shortcode = generate_shortcode(db)
        return insert_shortcode_into_db(db, url, shortcode)
    elif not re.match(r'^[a-zA-Z0-9_]{6,255}$', shortcode):
        return 412, 'The provided shortcode is invalid'
    else:
        db_shortcode = get_shortcode_from_db(db, shortcode)

        if db_shortcode:
            return 409, 'Shortcode already in use'
        else:
            return insert_shortcode_into_db(db, url, shortcode)


def insert_shortcode_into_db(db, url, shortcode):
    """ Insert function to insert shortcode into database """
    sql = 'INSERT INTO short_urls (url, shortcode) VALUES (?, ?)'
    values = (url, shortcode)
    db.execute(sql, values)
    db.commit()
    return 201, get_shortcode_from_db(db, shortcode)[1]


def get_shortcode_from_db(db, shortcode):
    """ Retriever fuction to retrieve shortcode and data from database (if existing) """
    sql = 'SELECT * FROM short_urls WHERE shortcode = ?'
    values = (shortcode,)
    return db.execute(sql, values).fetchone()


def generate_shortcode(db):
    """ Shortcode randomizer. Checks after randomization if shortcode exists"""
    shortcode = ""

    while not shortcode:
        shortcode = ''.join(choices(string.ascii_letters + string.digits, k=6))
        if get_shortcode_from_db(db, shortcode):  # pragma: no cover
            shortcode = ""

    return shortcode


def update_redirect_stats_in_db(db, shortcode):
    """ Function to update statistics when redirect has been requested """
    sql = "UPDATE short_urls SET redirect_count=redirect_count+1, "\
          "last_redirect=STRFTIME('%Y-%m-%d %H:%M:%f','NOW') WHERE shortcode = ?"
    values = (shortcode,)
    db.execute(sql, values)
    db.commit()

    return get_shortcode_from_db(db, shortcode)
