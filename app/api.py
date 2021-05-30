from flask import Blueprint, request, jsonify
import http
import requests
import simplejson as json
from datetime import datetime
from functools import wraps

from app.db import get_events, insert_events, get_location
from app.logger import log
from app.objects import Event

api_bp = Blueprint('api_bp', __name__)


def json_response(fn):
    @wraps(fn)
    def inner(args, **kwargs):
        response = fn(args, **kwargs)
        return jsonify(response)

    return inner


@api_bp.route("/")
@api_bp.route("/status")
def status():
    return '', http.HTTPStatus.OK


@api_bp.route('/refresh', methods=['POST'])
def refresh():
    try:
        location = request.args.get('location')
        start_time = request.args.get('start')
        end_time = request.args.get('end')
        ignore = request.args.get('ignore')
        if ignore == 'true':
            param = {'starttime': start_time, 'endtime': end_time,
                     'minmagnitude': '0.1', 'orderby': 'time'}
        else:
            eq_location = get_location(location)
            if eq_location.name:
                param = {'starttime': start_time, 'endtime': end_time,
                         'maxlatitude': eq_location.northeast_lat, 'minlatitude': eq_location.southwest_lat,
                         'maxlongitude': eq_location.northeast_lng, 'minlongitude': eq_location.southwest_lng,
                         'minmagnitude': '0.1', 'orderby': 'time'}
            else:
                return '', http.HTTPStatus.BAD_REQUEST

        response = requests.get(
            'https://earthquake.usgs.gov/fdsnws/event/1/query.geojson',
            params=param,
        )
        log.info('URL requested {}'.format(response.url))
        response_events = json.loads(response.text)
        record_list = []
        for event in response_events['features']:
            event_id = event['id']
            event_longitude = event['geometry']['coordinates'][0]
            event_latitude = event['geometry']['coordinates'][1]
            event_depth = event['geometry']['coordinates'][2]
            event_mag = event['properties']['mag']
            event_place = event['properties']['place']
            event_status = event['properties']['status']
            event_time = datetime.fromtimestamp(event['properties']['time'] / 1000.0)
            event_type = event['properties']['type']
            event_updated = datetime.fromtimestamp(
                event['properties']['updated'] / 1000.0)
            record_list.append(Event(event_id, event_longitude, event_latitude, event_depth, event_mag,
                                     event_place, event_status, event_time, event_type, event_updated))
        if record_list:
            insert_events(record_list)
            return '', http.HTTPStatus.CREATED
        else:
            return '', http.HTTPStatus.NO_CONTENT
    except Exception as error:
        log.error('Failed to request data {}'.format(error))


@api_bp.route('/events', methods=['GET'])
def events():
    try:
        location = request.args.get('location')
        start_time = request.args.get('start')
        end_time = request.args.get('end')
        min_mag = float(request.args.get('min'))
        if None not in (location, start_time, end_time, min_mag):
            date_format = '%Y-%m-%d %H:%M:%S'
            delta = datetime.strptime(end_time, date_format) - datetime.strptime(start_time, date_format)
            eq_location = get_location(location)
            if eq_location.name:
                eq_events = get_events(eq_location, start_time, end_time, min_mag)
            else:
                return '', http.HTTPStatus.BAD_REQUEST
            if eq_events:
                max_mag = 0
                max_time = datetime.now()
                min_mag = 100
                min_time = datetime.now()
                low_count = 0
                medium_count = 0
                high_count = 0
                for event in eq_events:
                    if event['mag'] > max_mag:
                        max_mag = event['mag']
                        max_time = event['time']
                    if event['mag'] < min_mag:
                        min_mag = event['mag']
                        min_time = event['time']
                    if event['mag'] < 4:
                        low_count += 1
                    if 4 <= event['mag'] <= 6:
                        medium_count += 1
                    if event['mag'] > 6:
                        high_count += 1

                total_count = len(eq_events)
                recent_mag = eq_events[total_count - 1]['mag']
                recent_time = eq_events[total_count - 1]['time']
                total_days = 'Nº Earthquakes since ' + str(delta.days) + ' day/s'

                events_max = {'value': max_mag, 'time': max_time}
                events_min = {'value': min_mag, 'time': min_time}
                events_recent = {'value': recent_mag, 'time': recent_time}
                events_total = {'value': total_count, 'time': total_days}
                events_count = {'low': low_count, 'medium': medium_count, 'high': high_count}
                map_location = {'lat': eq_location.lat, 'lng': eq_location.lng}

                response = {'events': eq_events, 'overview': {'max': events_max, 'min': events_min,
                                                              'recent': events_recent, 'total': events_total},
                            'count': events_count,
                            'map': map_location}
                return jsonify(response)
            return '', http.HTTPStatus.NO_CONTENT
        return '', http.HTTPStatus.BAD_REQUEST

    except Exception as error:
        print(error)
        log.error('Failed to retrieve events {}'.format(error))
