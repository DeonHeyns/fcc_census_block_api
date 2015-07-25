__author__ = 'DeonHeyns'

# -*- coding: utf-8 -*-

import requests
import json as jason


class Client(object):
    def __init__(self):
        self._domain = 'http://data.fcc.gov/api'
        self._params = None
        self._url = None
        self._response = None

    def execute(self):
        url = self._domain + self._url
        self._response = requests.get(url, params=self._params)
        return self

    @property
    def response(self):
        return self._response


class CensusBlockClient(Client):
    def __init__(self):
        Client.__init__(self)
        self._params = {}
        self._url = '/block/find'
        self._zipcode = None

    def latitude(self, latitude):
        self._params['latitude'] = latitude
        return self

    def longitude(self, longitude):
        self._params['longitude'] = longitude
        return self

    def show_all(self, show_all=True):
        self._params['showall'] = str(show_all).lower()
        return self

    def zipcode(self, zipcode):
        self._zipcode = zipcode
        return self

    def as_json(self):
        self.__set_format('json')
        return self

    def as_jsonp(self):
        self.__set_format('jsonp')
        return self

    def as_xml(self):
        self.__set_format('xml')
        return self

    def execute(self):
        if 'format' not in self._params:
            self.as_json()

        super(CensusBlockClient, self).execute()
        return BlockResponse(json=self.response.json(),
                             latitude=self._params['latitude'],
                             longitude=self._params['longitude'],
                             zipcode=self._zipcode)

    def __set_format(self, content_format='json'):
        self._params['format'] = content_format
        return self


class BlockResponse(object):
    def __init__(self, json, latitude, longitude, zipcode=None):
        self._block = ''
        self._county = ''
        self._state = ''
        self._message = ''
        self._status = ''
        self._executionTime = ''
        self._latitude = latitude
        self._longitude = longitude
        self._zipcode = zipcode
        self.__from_json(json)
        self._json = jason.dumps(json)

    def __from_json(self, json):
        self._status = str(json['status'])
        self._executionTime = str(json['executionTime'])
        self._county = County(fips=json['County']['FIPS'], name=json['County']['name'])
        self._state = State(fips=json['State']['FIPS'], code=json['State']['code'], name=json['State']['name'])
        self._message = '' if 'message' not in json else str('\r\n'.join(json['messages']))
        self._block = Block(fips=json['Block']['FIPS'])
        if 'intersection' in json['Block']:
            for intersection in json['Block']['intersection']:
                self._block.intersections.append(Intersection(fips=intersection['FIPS']))
        return self

    @property
    def block(self):
        return self._block

    @property
    def county(self):
        return self._county

    @property
    def state(self):
        return self._state

    @property
    def message(self):
        return self._message

    @property
    def status(self):
        return self._status

    @property
    def executionTime(self):
        return self._executionTime

    @property
    def json(self):
        additive = "{" + '"Zipcode": "{}", "Latitude": "{}", "Longitude": "{}", '.format(self.zipcode,
                                                                                         self._latitude,
                                                                                         self.longitude)
        self._json = self._json.replace('{', additive, 1)
        return self._json

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def zipcode(self):
        return self._zipcode


class Block(object):
    def __init__(self, fips):
        self._fips = str(fips)
        self._intersections = []

    @property
    def fips(self):
        return self._fips

    @property
    def intersections(self):
        return self._intersections


class Intersection(object):
    def __init__(self, fips):
        self._fips = str(fips)

    @property
    def fips(self):
        return self._fips


class County(object):
    def __init__(self, fips, name):
        self._fips = str(fips)
        self._name = str(name)

    @property
    def fips(self):
        return self._fips

    @property
    def name(self):
        return self._name


class State(object):
    def __init__(self, fips, code, name):
        self._fips = str(fips)
        self._code = str(code)
        self._name = str(name)

    @property
    def fips(self):
        return self._fips

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name