import mariadb
import googlemaps

from app.logger import log
from config import HOST, DATABASE, PORT, USER, PASSWORD, GEOCODING_API
from app.objects import Event, Location


def connect():
    try:
        connection = mariadb.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             port=PORT,
                                             password=PASSWORD)
        log.info('Connection opened')
        return connection
    except Exception as error:
        log.error('Connection failed: {}'.format(error))


def insert_events(records):
    connection = connect()
    cursor = connection.cursor()
    try:
        for record in records:
            try:
                query = '''INSERT IGNORE INTO events (id, longitude, latitude, 
                      depth, mag, place, status, time, type, updated) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
                record_tuple = (record.id, record.longitude, record.latitude,
                                record.depth, record.mag, record.place, record.status,
                                record.time, record.type, record.updated)
                cursor.execute(query, record_tuple)
            except ValueError as error:
                log.error(
                    'Failed to insert record in events table {}'.format(error))
        connection.commit()
        log.info('Records inserted successfully into table')
    except Exception as error:
        log.error('Failed to insert into events table {}'.format(error))
    finally:
        cursor.close()
        connection.close()
        log.info('Connection closed')


def get_events(location, start_time, end_time, min_mag):
    connection = connect()
    cursor = connection.cursor()
    try:
        events_list = []
        query = '''SELECT id, longitude, latitude, depth, mag,
                place, status, time, type, updated  FROM events 
                WHERE mag >= %s AND time BETWEEN %s AND %s AND latitude BETWEEN %s AND %s 
                AND longitude BETWEEN %s AND %s order by time asc'''
        cursor.execute(query, (min_mag, start_time, end_time, location.southwest_lat, location.northeast_lat,
                               location.southwest_lng, location.northeast_lng))
        rows = cursor.fetchall()
        for row in rows:
            events_list.append(Event(row[0], row[1], row[2], row[3], row[4],
                                     row[5], row[6], row[7], row[8], row[9]).__dict__)
        log.info('Records retrieved successfully from events table')
        return events_list
    except Exception as error:
        log.error('Failed to get events {}'.format(error))
    finally:
        cursor.close()
        connection.close()
        log.info('Connection closed')


def insert_location(record):
    connection = connect()
    cursor = connection.cursor()
    try:
        query = '''INSERT IGNORE INTO locations (name, lat, lng, northeast_lat,
                   northeast_lng, southwest_lat, southwest_lng) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s) '''
        record_tuple = (record.name, record.lat, record.lng, record.northeast_lat,
                        record.northeast_lng, record.southwest_lat, record.southwest_lng)
        cursor.execute(query, record_tuple)
        connection.commit()
        log.info('Geocode inserted successfully into table')
        return record
    except Exception as error:
        log.error('Failed to insert into locations table {}'.format(error))
    finally:
        cursor.close()
        connection.close()
        log.info('Connection closed')


def get_location(location_name):
    connection = connect()
    cursor = connection.cursor()
    try:
        name = location_name.lower()
        query = '''SELECT name, lat, lng, northeast_lat, northeast_lng,
                southwest_lat, southwest_lng FROM locations 
                WHERE name = %s'''
        cursor.execute(query, (name,))
        row = cursor.fetchone()
        if row:
            log.info('Geocode fetched successfully from table')
            return Location(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        maps = googlemaps.Client(key=GEOCODING_API)
        geocode_result = maps.geocode(name)
        log.info('Geocode requested')
        if geocode_result:
            coordinates = geocode_result[0]['geometry']['viewport']
            northeast_lat = coordinates['northeast']['lat']
            northeast_lng = coordinates['northeast']['lng']
            southwest_lat = coordinates['southwest']['lat']
            southwest_lng = coordinates['southwest']['lng']
            coordinates = geocode_result[0]['geometry']['location']
            lat = coordinates['lat']
            lng = coordinates['lng']
            insert_location(Location(name, lat, lng, northeast_lat, northeast_lng, southwest_lat, southwest_lng))
            return Location(name, lat, lng, northeast_lat, northeast_lng, southwest_lat, southwest_lng)
        return Location('', '', '', '', '', '', '')
    except Exception as error:
        log.error('Failed to get location geocode {}'.format(error))
    finally:
        cursor.close()
        connection.close()
        log.info('Connection closed')
