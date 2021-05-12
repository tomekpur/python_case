import time
from random import choices
from string import ascii_uppercase, digits

from url_shortner.database import get_db
from url_shortner.functions import generate_shortcode, get_shortcode_from_db, insert_shortcode_into_db, \
    validated_shortcode_insert, update_redirect_stats_in_db
import re


def test_validated_shortcode_insert(app):
    with app.app_context():
        # Configurations
        unused_valid_shortcode = 'xyz123'
        invalid_shortcode_char = '!N>@L|D'
        invalid_shortcode_short = 'abcde'
        valid_shortcode_short = ''.join('a' for _ in range(6))
        invalid_shortcode_long = ''.join('a' for _ in range(256))
        valid_shortcode_long = ''.join('a' for _ in range(255))
        url = 'https://somesite.com'
        used_shortcode = 'abc_12'

        # Setup
        generated_shortcode = validated_shortcode_insert(get_db(), url, '')
        insert_shortcode_into_db(get_db(), url, used_shortcode)

        # Assertions
        assert validated_shortcode_insert(get_db(), url, invalid_shortcode_char) == \
               (412, 'The provided shortcode is invalid')
        assert validated_shortcode_insert(get_db(), url, invalid_shortcode_short) == \
               (412, 'The provided shortcode is invalid')
        assert validated_shortcode_insert(get_db(), url, invalid_shortcode_long) == \
               (412, 'The provided shortcode is invalid')
        assert validated_shortcode_insert(get_db(), url, used_shortcode) == \
               (409, 'Shortcode already in use')
        assert validated_shortcode_insert(get_db(), url, unused_valid_shortcode) == (201, 'xyz123')
        assert validated_shortcode_insert(get_db(), url, valid_shortcode_short) == \
               (201, ''.join('a' for _ in range(6)))
        assert validated_shortcode_insert(get_db(), url, valid_shortcode_long) == \
               (201, ''.join('a' for _ in range(255)))
        assert generated_shortcode[0] == 201
        assert re.match(r'^[a-zA-Z0-9_]{6}$', generated_shortcode[1])


def test_insert_shortcode_into_db(app):
    with app.app_context():
        url = 'https://somesite.com'
        shortcode = 'qrs_123'

        inserted_shortcode = insert_shortcode_into_db(get_db(), url, shortcode)

        assert inserted_shortcode == (201, shortcode)


def test_generate_shortcode(app):
    with app.app_context():
        generated_shortcode = generate_shortcode(get_db())

        assert re.match(r'^[a-zA-Z0-9_]{6}$', generated_shortcode)


def test_get_shortcode_from_db(app):
    with app.app_context():
        url = 'https://somesite.com'
        shortcode = 'qrs_123'

        insert_shortcode_into_db(get_db(), url, shortcode)
        retreived_shortcode = get_shortcode_from_db(get_db(), shortcode)

        assert shortcode == retreived_shortcode[1]


def test_update_redirect_stats_in_db(app):
    with app.app_context():
        url = 'https://somesite.com'
        shortcode = 'nop_123'

        insert_shortcode_into_db(get_db(), url, shortcode)
        first_call = update_redirect_stats_in_db(get_db(), shortcode)
        time.sleep(0.1)
        second_call = update_redirect_stats_in_db(get_db(), shortcode)

        assert first_call[4] + 1 == second_call[4]
        assert first_call[3] < second_call[3]