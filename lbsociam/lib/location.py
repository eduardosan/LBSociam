#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import json
import re
from lbsociam.model import gmaps
from googlemaps.exceptions import ApiError, TransportError, Timeout
from lbsociam.model import location as loc

log = logging.getLogger()


def get_location(status, cache=True):
    """
    Get location for status
    :param status: status dict
    :param cache: Use cache to store and retrieve results
    :return: status with location
    """
    log.debug("LOCATION: processing id_doc = %s", status['_metadata']['id_doc'])
    source = json.loads(status['source'])
    source = source[0]
    status['location'] = dict()
    location_base = loc.LocationBase()

    geo = source.get('_geo')
    if geo is not None:
        latitude = geo['coordinates'][0]
        longitude = geo['coordinates'][1]

        status['location']['latitude'] = latitude
        status['location']['longitude'] = longitude

        # Register source
        status['location']['loc_origin'] = 'geo'

        return status

    coordinates = source.get('_coordinates')
    if coordinates is not None:
        # Try Coordinates
        status['location']['latitude'] = coordinates[0]
        status['location']['longitude'] = coordinates[1]

        # Register source
        status['location']['loc_origin'] = 'coordinates'

        return status

    location = source.get('_location')
    if location is not None:
        # Try to use cache first
        if cache:
            result = location_base.get_location(location)
            if result is None:
                result = maps_search(location)
            else:
                # Just return stored values
                status['location'] = result
                return status
        else:
            result = maps_search(location)
            
        if result is not None:
            status['location']['latitude'] = result['latitude']
            status['location']['longitude'] = result['longitude']
            status['location']['city'] = result['location']

            # Register source
            status['location']['loc_origin'] = 'location'

            return status

    # Try to consider user location
    user = source.get('_user')
    if user is not None:
        geo = user.get('_geo')
        if geo is not None:
            latitude = geo['coordinates'][0]
            longitude = geo['coordinates'][1]

            status['location']['latitude'] = latitude
            status['location']['longitude'] = longitude

            # Register source
            status['location']['loc_origin'] = 'user_geo'

            return status

        coordinates = user.get('_coordinates')
        if coordinates is not None:
            # Try Coordinates
            status['location']['latitude'] = coordinates[0]
            status['location']['longitude'] = coordinates[1]

            # Register source
            status['location']['loc_origin'] = 'user_coordinates'

            return status

        location = user.get('_location')
        if location is not None:
            # Try to use cache first
            if cache:
                result = location_base.get_location(location)
                if result is None:
                    result = maps_search(location)
                else:
                    # Just return stored values
                    status['location'] = result
                    return status
            else:
                result = maps_search(location)

            if result is not None:
                status['location']['latitude'] = result['latitude']
                status['location']['longitude'] = result['longitude']
                status['location']['city'] = result['location']

                # Register source
                status['location']['loc_origin'] = 'user_location'

                return status

    # Last try: use SRL to find location
    for structure in status['arg_structures']:
        for argument in structure['argument']:
            argument_name = argument['argument_name']
            log.debug("LOCATION: search in argument_name = %s", argument_name)

            if re.match('.*-LOC', argument_name) is not None:
                log.debug("LOCATION: string match for argument_name = %s", argument_name)
                # Try to use cache first
                if cache:
                    result = location_base.get_location(location)
                    if result is None:
                        result = maps_search(location)
                    else:
                        # Just return stored values
                        status['location'] = result
                        return status
                else:
                    result = maps_search(argument['argument_value'])

                if result is not None:
                    status['location']['latitude'] = result['latitude']
                    status['location']['longitude'] = result['longitude']
                    status['location']['city'] = result['location']

                    # Register source
                    status['location']['loc_origin'] = 'srl'

                    return status

    # If I'm here, it was not possible to find the location
    log.error("Location not found for status id = %s", status['_metadata']['id_doc'])
    del status['location']

    return status


def maps_search(location):
    """
    Search for location in Google Maps API
    :param location: text location identified
    :return: dict with latitude and longitude
    """
    log.debug("SEARCH: location %s", location)
    maps = gmaps.GMaps()
    try:
        result = maps.client.geocode(location)
        if len(result) == 0:
            return None
    except ApiError as e:
        log.error("Location not found\n%s", e)
        return None
    except TransportError as e:
        log.error("Location not found\n%s", e)
        return None
    except Timeout as e:
        log.error("Location not found\n%s", e)
        return None

    # As a start, select first random result
    try:
        lat = result[0]['geometry']['location']['lat']
        lng = result[0]['geometry']['location']['lng']
        loc = result[0]['address_components'][0]['long_name']
    except IndexError as e:
        log.error("Invalid results %s\n%s", result, e)
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']
        loc = result['address_components'][0]['long_name']

    result_dict = {
        'latitude': lat,
        'longitude': lng,
        'location': loc
    }

    log.debug("SEARCH: result dict: %s", result_dict)

    return result_dict