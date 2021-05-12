import ast
import json

from url_shortner.database import get_db
from url_shortner.functions import insert_shortcode_into_db, get_shortcode_from_db
import re


def test_shorten(app, client):
    with app.app_context():
        # Configurations
        url = 'https://somesite.com'
        shortcode = 'xyz_01'

        # Setup
        new_shortcode_request = client.post('shorten', json={'url': url, 'shortcode': shortcode})
        new_shortcode_json = ast.literal_eval(new_shortcode_request.data.decode('utf-8'))

        missing_shortcode_request = client.post('shorten', json={'url': url})
        missing_shortcode_generated = json.loads(missing_shortcode_request.data.decode('utf8'))['shortcode']

        empty_shortcode_request = client.post('shorten', json={'url': url, 'shortcode': ''})
        empty_shortcode_generated = json.loads(empty_shortcode_request.data.decode('utf8'))['shortcode']

        incorrect_header_request = client.post('shorten')

        blank_url_request = client.post('shorten', json={'url': '', 'shortcode': 'abc_01'})
        missing_url_request = client.post('shorten', json={'shortcode': 'abc_01'})

        shortcode_in_use_request = client.post('shorten', json={'url': url, 'shortcode': shortcode})

        invalid_shortcode_request = client.post('shorten', json={'url': url, 'shortcode': '!N>@L|D'})

        # Assertions
        assert new_shortcode_request.status_code == 201
        assert new_shortcode_json == {'shortcode': shortcode}

        assert missing_shortcode_request.status_code == 201
        assert re.match(r'^[a-zA-Z0-9_]{6}$', missing_shortcode_generated)

        assert empty_shortcode_request.status_code == 201
        assert re.match(r'^[a-zA-Z0-9_]{6}$', empty_shortcode_generated)

        assert incorrect_header_request.status_code == 400
        assert incorrect_header_request.data == b'Content-Type-header not "application/json"'

        assert blank_url_request.status_code == 400
        assert blank_url_request.data == b'Url not present'

        assert missing_url_request.status_code == 400
        assert missing_url_request.data == b'Url not present'

        assert shortcode_in_use_request.status_code == 409
        assert shortcode_in_use_request.data == b'Shortcode already in use'

        assert invalid_shortcode_request.status_code == 412
        assert invalid_shortcode_request.data == b'The provided shortcode is invalid'


def test_redirect(app, client):
    with app.app_context():
        url = 'https://somesite.com'
        shortcode = 'xyz_02'

        insert_shortcode_into_db(get_db(), url, shortcode)
        valid_redirect_request = client.get(shortcode)
        invalid_redirect_request = client.get('non-existing-shortcode')

        assert valid_redirect_request.status_code == 302
        assert valid_redirect_request.headers['Location'] == url

        assert invalid_redirect_request.status_code == 404
        assert invalid_redirect_request.data == b'Shortcode not found'


def test_stats(app, client):
    with app.app_context():
        # Configurations
        url = 'https://somesite.com'
        shortcode = 'xyz_03'

        # Setup
        insert_shortcode_into_db(get_db(), url, shortcode)

        retreived_shortcode = get_shortcode_from_db(get_db(), shortcode)
        created_first = retreived_shortcode[2].isoformat(timespec='milliseconds') + 'Z'
        redirect_count_first = retreived_shortcode[4]
        valid_stat_request_first = client.get(shortcode + '/stats')
        valid_stat_json_first = ast.literal_eval(valid_stat_request_first.data.decode('utf-8'))

        client.get(shortcode)  # Simulate a redirect request

        retreived_shortcode = get_shortcode_from_db(get_db(), shortcode)
        created_second = retreived_shortcode[2].isoformat(timespec='milliseconds') + 'Z'
        last_redirect_second = retreived_shortcode[3].isoformat(timespec='milliseconds') + 'Z'
        redirect_count_second = retreived_shortcode[4]

        valid_stat_request_second = client.get(shortcode + '/stats')
        valid_stat_json_second = ast.literal_eval(valid_stat_request_second.data.decode('utf-8'))

        invalid_stat_request = client.get('non-existing-shortcode/stats')

        # Assertions
        assert valid_stat_request_first.status_code == 200
        assert valid_stat_json_first == \
               {'created': created_first, 'redirectCount': redirect_count_first}

        assert valid_stat_request_second.status_code == 200
        assert valid_stat_json_second == \
               {'created': created_second, 'lastRedirect': last_redirect_second, 'redirectCount': redirect_count_second}

        assert invalid_stat_request.status_code == 404
        assert invalid_stat_request.data == b'Shortcode not found'
