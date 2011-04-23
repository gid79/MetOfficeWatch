from sets import Set
from google.appengine.ext import db
import datetime

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

class DictModel(db.Model):
    #noinspection PyDefaultArgument
    def to_dict(self, excluding = []):
        output = {}
        exclude_props = Set(excluding)
        for key, prop in self.properties().iteritems():
            if key not in exclude_props:
                value = getattr(self, key)

                if value is None or isinstance(value, SIMPLE_TYPES):
                    output[key] = value
                elif isinstance(value, datetime.date):
                    # Convert date/datetime to ms-since-epoch ("new Date()").
    #                ms = time.mktime(value.utctimetuple()) * 1000
    #                ms += getattr(value, 'microseconds', 0) / 1000
                    output[key] = value.isoformat()
                elif isinstance(value, db.GeoPt):
                    output[key] = {'lat': value.lat, 'lon': value.lon}
                elif isinstance(value, db.Model):
                    output[key] = value.to_dict()
                else:
                    raise ValueError('cannot encode ' + repr(prop))

        output['id'] = self.key().id_or_name()
        return output

class Site(DictModel):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    region = db.StringProperty()

class Forecast:
    site = db.ReferenceProperty(reference_class=Site)
    forecast_date = db.DateProperty()
#    issued_datetime

class ForecastTimestep(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    forecast_datetime = db.DateTimeProperty()
    forecast_date = db.DateProperty()
    issued_datetime = db.DateTimeProperty()

    feels_like_temperature = db.IntegerProperty()
    temperature = db.IntegerProperty()
    max_uv_index = db.IntegerProperty()
    wind_gust = db.IntegerProperty()
    pressure = db.IntegerProperty()
    screen_relative_humidity = db.IntegerProperty()
    weather_type = db.IntegerProperty()
    visibility = db.IntegerProperty()
    wind_direction = db.StringProperty()
    wind_speed = db.IntegerProperty()

    @classmethod
    def find_by_site_and_dates(cls, site, forecast_date, issued_date):
        q = ForecastTimestep.all()
        q.filter("site =", site)
        q.filter("forecast_datetime =", forecast_date)
        q.filter("issued_datetime =", issued_date)

        return q.get()

class ObservationTimestep(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    observation_datetime = db.DateTimeProperty()
    observation_date = db.DateProperty()

    wind_gust = db.IntegerProperty()
    wind_speed = db.IntegerProperty()
    wind_direction = db.StringProperty()
    pressure = db.IntegerProperty()
    pressure_tendency = db.StringProperty()
    screen_relative_humidity = db.IntegerProperty()
    weather_type = db.IntegerProperty()
    temperature = db.FloatProperty()
    visibility = db.IntegerProperty()

    @classmethod
    def find_by_site_and_date(cls, site, date):
        q = (ObservationTimestep.all()
                .filter("site =", site)
                .filter("observation_datetime =", date))
        return q.get()

    @classmethod
    def find_latest_by_site(cls, site, limit = 100):
        q = (ObservationTimestep.all()
                .filter("site =", site)
                .order("-observation_datetime"))

        return q.fetch(limit = limit)