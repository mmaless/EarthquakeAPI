class Event:
    def __init__(self, event_id, event_longitude, event_latitude, event_depth,
                 event_mag, event_place, event_status, event_time, event_type, event_updated):
        self.id = event_id
        self.longitude = event_longitude
        self.latitude = event_latitude
        self.depth = event_depth
        self.mag = event_mag
        self.place = event_place
        self.status = event_status
        self.time = event_time
        self.type = event_type
        self.updated = event_updated


class Location:
    def __init__(self, name, lat, lng, northeast_lat, northeast_lng,
                 southwest_lat, southwest_lng):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.northeast_lat = northeast_lat
        self.northeast_lng = northeast_lng
        self.southwest_lat = southwest_lat
        self.southwest_lng = southwest_lng