from datetime import datetime, timedelta
import requests
import simplejson as json

from app.objects import Event
from app.db import insert_events
from app.logger import log


def job():
    try:
        d1 = datetime.now() + timedelta(days=-1)
        d2 = datetime.now()
        start_time = d1.strftime('%Y-%m-%d %H:%M:%S')
        end_time = d2.strftime('%Y-%m-%d %H:%M:%S')
        param = {'starttime': start_time, 'endtime': end_time,
                 'minmagnitude': '0.1', 'orderby': 'time'}
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
            return True
        return False
    except Exception as error:
        log.error('Failed to request data {}'.format(error))
