"""Download files from the FCC for stations defined in the database, or pulled live from data.fcc.gov."""

import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
import util
import dbutil
import settings as st
import shutil
import us
from random import shuffle


LIVE_STATIONS = True


def processRec(url):
    dirs = url.split('/')
    rec = {}

    rec['stationid'] = dirs[2]
    rec['year'] = dirs[4]
    rec['type'] = dirs[5]
    rec['url'] = url

    if dirs[5] == 'Federal':
        rec['office'] = dirs[6]

    return rec


def convertDictToInsert(d, table):
    values = ', '.join(['%s'] * len(d))
    # Prebind these, psycopg only accepts values
    fields = values % tuple(d.keys())

    return "INSERT INTO %s (%s) VALUES (%s)" % (table, fields, values)


def dbInsert(d, table):
    (conn, cur) = dbutil.connect()
    stmt = convertDictToInsert(d, table)
    cur.execute(stmt, d.values())
    conn.commit()
    dbutil.disconnect(conn)


def updateStationState(station, state):
    (conn, cur) = dbutil.connect()
    cur.execute(
        ''' UPDATE station set state = %s where station = %s ''', (state, station))
    conn.commit()
    dbutil.disconnect(conn)


def updateStation(station):
    (conn, cur) = dbutil.connect()
    cur.execute(
        ''' UPDATE station set updated = %s where station = %s ''', (datetime.now(), station))
    conn.commit()
    dbutil.disconnect(conn)


def getFilenameFromUrl(url):
    fullpath = url.split('/')
    return '/'.join(fullpath[4:])

if LIVE_STATIONS:
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

else:

    (conn, cur) = dbutil.connect()
    cur.execute(
        ''' SELECT station FROM station where updated < '2015-01-03' ''')
    station_rows = cur.fetchall()
    shuffle(station_rows)
    stations = [item for sublist in station_rows for item in sublist]


for station in stations:

    print station
    url = '''https://stations.fcc.gov/station-profile/%s/rss/''' % (station)

    req = urllib2.Request(url=url)

    db = open('logs/db.txt', 'a')
    log = open('logs/station_dloader.log', 'a')

    f = urllib2.urlopen(req)
    page = BeautifulSoup(f.read())

    for entry in page.find_all('entry'):
        for link in entry.content.div.p.find_all('a'):
            if link.get_text() == 'here' and 'Political File/' + str(st.YEAR) in link.get('href'):
                url = link.get('href')
                fullURL = st.baseurl + url
                filename = st.basepath + 'html/' + getFilenameFromUrl(fullURL)

                if filename[-3:].lower() != 'pdf':
                    continue

                outputFile = filename[:-3] + 'html'

                if not os.path.exists(outputFile):
                    print outputFile
                    try:
                        if not os.path.exists(os.path.dirname(filename)):
                            os.makedirs(os.path.dirname(filename))

                        util.downloadBinary(fullURL, filename)

                        util.pdfToText(filename)

                        rec = processRec(url)
                        rec['id'] = entry.id.get_text().replace(
                            ':', '_').replace(')', '')
                        rec['station'] = rec['id'].split('_')[0]
                        rec['updated'] = entry.updated.get_text()
                        #rec['outfile'] = outputFile

                        db.write(json.dumps(rec) + '\n')

                        dbInsert(rec, 'polfile')
                        pdfpath = '%spdfs/%s.pdf' % (st.basepath, rec['id'])
                        shutil.move(filename, pdfpath)
                    except Exception, e:
                        log.write(outputFile.encode('ascii', 'ignore') + '\n')
                        log.write(str(e))
                        log.write('-------------------\n\n')
    updateStation(station)
    db.close()
    log.close()
