from flask import Blueprint, request, make_response

from url_shortner.database import get_db
from url_shortner.functions import validated_shortcode_insert, get_shortcode_from_db, update_redirect_stats_in_db

bp = Blueprint('shortner', __name__, url_prefix='/')


@bp.route('shorten', methods=['POST'])
def post_request_shorten():
    """ Route to enter a new shortcode in the database, including validations """
    db = get_db()

    # Only accept application/json
    if request.headers.get('Content-Type') != 'application/json':
        return 'Content-Type-header not "application/json"', 400

    body = request.json

    try:  # Try to catch bodies without url
        url = body['url']
    except KeyError:
        url = ''

    if not url:  # Return 'Bad request' if url is not in input
        response = make_response('Url not present', 400)
    else:
        try:  # Try to catch bodies without shortcode
            shortcode = body['shortcode']
        except KeyError:
            shortcode = ''

        validated_shortcode = validated_shortcode_insert(db, url, shortcode)

        if validated_shortcode[0] == 409:  # Return 'Conflict' Shortcode in use
            response = make_response(validated_shortcode[1], validated_shortcode[0])
        elif validated_shortcode[0] == 412:  # Return 'Precondition failed' is shortcode is in invalid format
            response = make_response(validated_shortcode[1], validated_shortcode[0])
        else:  # Return 'Created' when inserted in db
            response = make_response({'shortcode': validated_shortcode[1]}, validated_shortcode[0])

    return response


@bp.route('<shortcode>', methods=['GET'])
def redirect(shortcode):
    """ Route to get a redirect for a shortcode """
    db = get_db()
    retrieved_shortcode = get_shortcode_from_db(db, shortcode)

    if not retrieved_shortcode:
        response = make_response('Shortcode not found', 404)
    else:
        update_redirect_stats_in_db(db, shortcode)
        response = make_response('', 302)
        response.headers['Location'] = retrieved_shortcode[0]

    return response


@bp.route('<shortcode>/stats', methods=['GET'])
def stats(shortcode):
    """ Route to get a redirect for a shortcode """
    db = get_db()
    retrieved_shortcode = get_shortcode_from_db(db, shortcode)

    if not retrieved_shortcode:
        response = make_response('Shortcode not found', 404)
    else:
        data = {
            'created': retrieved_shortcode[2].isoformat(timespec='milliseconds') + 'Z',
            'redirectCount': retrieved_shortcode[4]
        }
        if retrieved_shortcode[3]:
            data['lastRedirect'] = retrieved_shortcode[3].isoformat(timespec='milliseconds') + 'Z'
        response = make_response(data, 200)

    return response
