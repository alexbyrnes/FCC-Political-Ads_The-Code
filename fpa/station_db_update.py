"""Update the database with new information on station call signs and states."""

import urllib2
import json
import dbutil
import us
from datetime import datetime

states = [s.abbr for s in us.states.STATES]
stations = []

for state in states:

    url = '''http://data.fcc.gov/mediabureau/v01/tv/facility/search/%s.json''' % (
        state)

    req = urllib2.Request(url=url)

    f = urllib2.urlopen(req)
    page = json.loads(f.read())
    facilities = [sl['facilityList'] if sl['searchType'] ==
                  'State' else None for sl in page['results']['searchList']]
    facilities = [fac for fac in facilities if fac is not None][0]
    for facility in facilities:
        stations.append(facility['callSign'])

stations.sort(reverse=False)

(conn, cur) = dbutil.connect()

for station in stations:

    print station
    cur.execute(
        ''' INSERT INTO station values (%s, %s) ''', (station, datetime.now()))
    conn.commit()

dbutil.disconnect(conn)
