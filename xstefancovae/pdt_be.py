#!/usr/bin/python
import random
import string
import psycopg2
import sys
import pprint
import json
import string
import cherrypy
cherrypy.config.update({'server.socket_port': 8099})

# Connection atributes
host='localhost'
dbname='pdtdb'
user='postgres'
password='nepoviem'
port=5433

def postgreConn(thread_index):
	print ("Connecting to database -> "+ dbname)
	# get a connection, if a connect cannot be made => an exception
	cherrypy.thread_data.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
	print ("Connected!\n")

cherrypy.engine.subscribe('start_thread', postgreConn)


class GeoGeneratorWebService(object):

	@cherrypy.expose
	def index(self):
		return 'Hello world'

	def createMyJson(self, cursor):
		records = []
		for record in cursor:
			records.append(record)
		print ("Records served\n")
		return(json.dumps(records).encode('utf8'))

	def ifGradient(self, gradient):
		print ("Gradient: true/false\n")
		if (gradient == 'true'):
			return('ORDER BY count DESC')
		return ''

	@cherrypy.expose
	def city_sport(self, location, gradient):
		# order all if gradient
		gradient_add = self.ifGradient(gradient)
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM 
				(SELECT DISTINCT st_asgeojson(t_loc.way), COUNT(t_loc.way) 
				FROM ( SELECT DISTINCT t_city.way 
					FROM ( SELECT l.way 
						FROM planet_osm_polygon as l 
						WHERE leisure IN ('sports_centre', 'stadium', 'track', 'pitch', 'swimming_pool', 'recreation_ground', 'golf_course', 'park') 
						OR sport IS NOT NULL 
					) as t_city 
					CROSS JOIN planet_osm_polygon as t1 
					WHERE to_tsvector('sk', t1.name) @@ to_tsquery('sk', '"""+location+"""') AND ST_Contains(t1.way, t_city.way) 
				) as t_city 
				CROSS JOIN ( SELECT DISTINCT t_roads.name, t_roads.way 
					FROM ( SELECT DISTINCT t1.name, t1.way 
						FROM planet_osm_line as t1 
						WHERE t1.highway IS NOT NULL 
						AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
						UNION 
						SELECT DISTINCT t1.name, t1.way 
						FROM planet_osm_polygon as t1 
						WHERE t1.highway IS NOT NULL 
						AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
					) as t_roads 
					CROSS JOIN planet_osm_polygon as t_place 
					WHERE to_tsvector('sk', t_place.name) @@ to_tsquery('sk', '"""+location+"""')
					AND ST_Contains(t_place.way, t_roads.way) 
				) as t_loc 
				WHERE ST_DWithin(t_loc.way::geography, t_city.way::geography, 10) 
				GROUP BY t_loc.way """+gradient_add+""") 
			as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

	@cherrypy.expose
	def city_life(self, location, gradient):
		# order all if gradient
		gradient_add = self.ifGradient(gradient)
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM (SELECT DISTINCT st_asgeojson(t_loc.way), COUNT(t_loc.way) 
				FROM ( SELECT DISTINCT t_city.way 
					FROM ( SELECT l.way 
						FROM planet_osm_polygon as l 
						WHERE l.amenity IN ('arts_centre', 'bar', 'biergarten', 'brothel', 'cafe', 'casino', 'cinema', 'community_centre', 'distillery', 'events_venue', 'fast_food', 'library', 'marketplace', 'nightclub', 'pub', 'restaurant', 'theatre') 
						OR l.leisure IS NOT NULL 
						OR l.shop IS NOT NULL ) as t_city 
						CROSS JOIN planet_osm_polygon as t1 
						WHERE to_tsvector('sk', t1.name) @@ to_tsquery('sk', '"""+location+"""') AND ST_Contains(t1.way, t_city.way) 
					) as t_city 
					CROSS JOIN ( SELECT DISTINCT t_roads.name, t_roads.way 
						FROM ( SELECT DISTINCT t1.name, t1.way 
							FROM planet_osm_line as t1 
							WHERE t1.highway IS NOT NULL 
							AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
							UNION 
							SELECT DISTINCT t1.name, t1.way 
							FROM planet_osm_polygon as t1 
							WHERE t1.highway IS NOT NULL 
							AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
						) as t_roads 
						CROSS JOIN planet_osm_polygon as t_place 
						WHERE to_tsvector('sk', t_place.name) @@ to_tsquery('sk', '"""+location+"""')
						AND ST_Contains(t_place.way, t_roads.way)  
					) as t_loc 
					WHERE ST_DWithin(t_loc.way::geography, t_city.way::geography, 10) 
					GROUP BY t_loc.way """+gradient_add+"""
				) as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

	@cherrypy.expose
	def city_tourism(self, location, gradient):
		# order all if gradient
		gradient_add = self.ifGradient(gradient)
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM (SELECT DISTINCT st_asgeojson(t_loc.way), COUNT(t_loc.way) 
				FROM ( SELECT DISTINCT t_city.way 
					FROM ( SELECT l.way FROM planet_osm_polygon as l 
					WHERE l.historic IS NOT NULL OR l.tourism IS NOT NULL 
				) as t_city 
				CROSS JOIN planet_osm_polygon as t1 
				WHERE to_tsvector('sk', t1.name) @@ to_tsquery('sk', '"""+location+"""') AND ST_Contains(t1.way, t_city.way) 
			) as t_city 
			CROSS JOIN ( SELECT DISTINCT t_roads.name, t_roads.way 
				FROM ( SELECT DISTINCT t1.name, t1.way 
					FROM planet_osm_line as t1 
					WHERE t1.highway IS NOT NULL 
					AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
					UNION 
					SELECT DISTINCT t1.name, t1.way 
					FROM planet_osm_polygon as t1 
					WHERE t1.highway IS NOT NULL 
					AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
				) as t_roads 
				CROSS JOIN planet_osm_polygon as t_place
				WHERE to_tsvector('sk', t_place.name) @@ to_tsquery('sk', '"""+location+"""')
				AND ST_Contains(t_place.way, t_roads.way)   
			) as t_loc 
			WHERE ST_DWithin(t_loc.way::geography, t_city.way::geography, 10) 
			GROUP BY t_loc.way """+gradient_add+"""
		) as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

	@cherrypy.expose
	def kids(self, location, gradient):
		# order all if gradient
		gradient_add = self.ifGradient(gradient)
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM (SELECT DISTINCT st_asgeojson(t_loc.way), COUNT(t_loc.way) 
				FROM ( SELECT DISTINCT t_kids.way 
					FROM ( SELECT DISTINCT t_kids.way 
						FROM planet_osm_polygon as t_kids 
						WHERE t_kids.building IN ('school', 'kindergarten') OR t_kids.leisure IN ('playground', 'park') 
						OR t_kids.amenity IN ('school', 'kindergarten') 
					) as t_kids 
					CROSS JOIN planet_osm_polygon as t1 
					WHERE to_tsvector('sk', t1.name) @@ to_tsquery('sk', '"""+location+"""') AND ST_Contains(t1.way, t_kids.way) 
				) as t_kids 
				CROSS JOIN ( SELECT DISTINCT t_roads.name, t_roads.way 
					FROM ( SELECT DISTINCT t1.name, t1.way 
						FROM planet_osm_line as t1 
						WHERE t1.highway IS NOT NULL 
						AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
						UNION SELECT DISTINCT t1.name, t1.way 
							FROM planet_osm_polygon as t1 
							WHERE t1.highway IS NOT NULL 
							AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
						) as t_roads 
						CROSS JOIN planet_osm_polygon as t_place 
						WHERE to_tsvector('sk', t_place.name) @@ to_tsquery('sk', '"""+location+"""')
						AND ST_Contains(t_place.way, t_roads.way) 
					) as t_loc 
					WHERE ST_DWithin(t_loc.way::geography, t_kids.way::geography, 50) 
					GROUP BY t_loc.way """+gradient_add+"""
				) as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

	@cherrypy.expose
	def public_transport(self, location, gradient):
		# order all if gradient
		gradient_add = self.ifGradient(gradient)
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM (SELECT DISTINCT st_asgeojson(t_loc.way), COUNT(t_loc.name) 
				FROM ( SELECT DISTINCT t.name, t.way 
					FROM ( SELECT DISTINCT t.name, t.way 
						FROM planet_osm_point as t 
						WHERE t.highway LIKE 'bus_stop' 
						UNION 
						SELECT DISTINCT t.name, t.way 
						FROM planet_osm_polygon as t 
						WHERE t.public_transport IS NOT NULL 
						UNION 
						SELECT DISTINCT t.name, t.way 
						FROM planet_osm_line as t 
						WHERE t.public_transport IS NOT NULL UNION SELECT DISTINCT t.name, t.way 
						FROM planet_osm_point as t WHERE t.public_transport IS NOT NULL
					) as t 
					CROSS JOIN planet_osm_polygon as t1 
					WHERE to_tsvector('sk', t1.name) @@ to_tsquery('sk', '"""+location+"""') AND ST_Contains(t1.way, t.way) 
				) as t_trans 
				CROSS JOIN 
				( SELECT DISTINCT t_roads.name, t_roads.way 
				FROM ( SELECT DISTINCT t1.name, t1.way 
					FROM planet_osm_line as t1 
					WHERE t1.highway IS NOT NULL 
					AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
					UNION 
					SELECT DISTINCT t1.name, t1.way FROM planet_osm_polygon as t1 
					WHERE t1.highway IS NOT NULL 
					AND t1.highway NOT IN ('raceway', 'trunk', 'trunk_link', 'construction', 'motorway', 'motorway_link', 'no', 'none', 'piste', 'proposed') 
				) as t_roads 
				CROSS JOIN planet_osm_polygon as t_place 
				WHERE to_tsvector('sk', t_place.name) @@ to_tsquery('sk', '"""+location+"""')
				AND ST_Contains(t_place.way, t_roads.way) 
			) as t_loc 
			WHERE ST_DWithin(t_loc.way::geography, t_trans.way::geography, 5) 
			GROUP BY t_loc.way """+gradient_add+"""
		) as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

	@cherrypy.expose
	def find_in(self, location, place):
		# cursor object for queries
		cursor = cherrypy.thread_data.conn.cursor() 
		# select
		cursor.execute("""SELECT row_to_json(t_final) 
			FROM (SELECT DISTINCT t.name, st_asgeojson(t.way) 
				FROM ( SELECT DISTINCT p2.name, p2.way::geography 
					FROM planet_osm_polygon as p1 
					CROSS JOIN planet_osm_polygon as p2 
					WHERE (ST_Contains(p1.way, p2.way) OR ST_Intersects(p1.way::geography, p2.way::geography)) 
					AND to_tsvector('sk', p1.name) @@ to_tsquery('sk', '"""+location+"""') AND to_tsvector('sk', p2.name) @@ to_tsquery('sk', '"""+place+"""')
					UNION 
					SELECT DISTINCT p2.name, p2.way::geography 
					FROM planet_osm_polygon as p1 
					CROSS JOIN planet_osm_line as p2 
					WHERE (ST_Contains(p1.way, p2.way) OR ST_Intersects(p1.way::geography, p2.way::geography)) 
					AND to_tsvector('sk', p1.name) @@ to_tsquery('sk', '"""+location+"""') AND to_tsvector('sk', p2.name) @@ to_tsquery('sk', '"""+place+"""') 
					UNION 
					SELECT DISTINCT p2.name, p2.way::geography 
					FROM planet_osm_polygon as p1 
					CROSS JOIN planet_osm_point as p2 
					WHERE (ST_Contains(p1.way, p2.way) OR ST_Intersects(p1.way::geography, p2.way::geography)) 
					AND to_tsvector('sk', p1.name) @@ to_tsquery('sk', '"""+location+"""') AND to_tsvector('sk', p2.name) @@ to_tsquery('sk', '"""+place+"""')
					UNION SELECT DISTINCT p2.name, p2.way::geography 
					FROM planet_osm_line as p1 
					CROSS JOIN planet_osm_point as p2 WHERE (ST_Contains(p1.way, p2.way) OR ST_Intersects(p1.way::geography, p2.way::geography)) 
					AND to_tsvector('sk', p1.name) @@ to_tsquery('sk', '"""+location+"""') AND to_tsvector('sk', p2.name) @@ to_tsquery('sk', '"""+place+"""')
				) as t
			) as t_final;""")
		# retrieve the records from the database
		return(self.createMyJson(cursor))

def CORS():
	cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
	cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST"
	cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"

if __name__ == '__main__':
	conf = {
		'/': {
			#'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True,
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'application/json')],
			'tools.CORS.on': True,
			'tools.encode.on': True,
    		'tools.encode.encoding': 'utf-8'
		}
	}
	cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
	cherrypy.quickstart(GeoGeneratorWebService(), '/', conf)