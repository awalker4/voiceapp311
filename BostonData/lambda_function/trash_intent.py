"""
Functions for Alexa responses related to trash day
"""

from alexa_utilities import build_response, build_speechlet_response
from streetaddress import StreetAddressParser
import requests
import alexa_constants


def get_trash_day_info(intent, session):
    """
    Generates response object for a trash day inquiry.
    """
    reprompt_text = None
    print("IN GET_TRASH_DAY_INFO, SESSION: " + str(session))

    if alexa_constants.CURRENT_ADDRESS_KEY in session.get('attributes', {}):
        current_address = \
            session['attributes'][alexa_constants.CURRENT_ADDRESS_KEY]

        # grab relevant information from session address
        address_parser = StreetAddressParser()
        a = address_parser.parse(current_address)
        # currently assumes that trash day is the same for all units at
        # the same street address
        address = str(a['house']) + " " + str(a['street_name'])

        # rest call to data.boston.gov for trash/recycle information
        url = 'https://data.boston.gov/api/action/datastore_search?' + \
              'resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q=' + \
              '{{"Address":"{}"}}'.format(address)
        resp = requests.get(url).json()
        print("RESPONSE FROM DATA.BOSTON.GOV: " + str(resp))

        # format script of response
        record = resp['result']['records'][0]
        speech_output = "Trash is picked up on the following days, " + \
            ", ".join(parse_days(record['Trash'])) + \
            ". Recycling is picked up on the following days, " + \
            " ,".join(parse_days(record['Recycling']))

        session_attributes = session.get('attributes', {})
        should_end_session = True
    else:
        session_attributes = session.get('attributes', {})
        speech_output = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def parse_days(days):
    """
    Converts the string of day initials in the JSON response to the trash
    day calendar API to a list of days.
    """
    result = []
    for i in range(len(days)):
        if days[i] == 'T':
            if i < len(days) - 1 and days[i+1] == 'H':
                result.append('Thursday')
            else:
                result.append('Tuesday')
        if days[i] == 'M':
            result.append('Monday')
        if days[i] == 'W':
            result.append('Wednesday')
        if days[i] == 'F':
            result.append('Friday')
    return result
