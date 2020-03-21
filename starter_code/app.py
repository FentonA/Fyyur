#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
		__tablename__ = 'Venue'

		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String)
		city = db.Column(db.String(120))
		state = db.Column(db.String(120))
		address = db.Column(db.String(120))
		phone = db.Column(db.String(120))
		image_link = db.Column(db.String(500))
		facebook_link = db.Column(db.String(120))
		genres = db.Column(db.String(120))
		phone = db.Column(db.String(120))
		wbesite = db.Column(db.String(120))
		seeking_talent = db.Column(db.Boolean)
		show = db.relationship('Show', backref='venue', lazy=True)
		# upcoming_shows
		# past_shows_count
		# upcoming_shows_count
		# TODO: implement any missing fields, as a database migration using
		# Flask-Migrate


class Artist(db.Model):
		__tablename__ = 'Artist'

		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String)
		city = db.Column(db.String(120))
		state = db.Column(db.String(120))
		phone = db.Column(db.String(120))
		genres = db.Column(db.String(120))
		image_link = db.Column(db.String(500))
		facebook_link = db.Column(db.String(120))
		seeking_venue = db.Column(db.Boolean)
		seeking_description = db.Column(db.String(150))
		image_link = db.Column(db.String(120))
		shows = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=True)
		show = db.relationship('Show', backref='artist', lazy=True)
		# upcoming_shows,
		# past_shows
		# upcoming_shows_count
		# TODO: implement any missing fields, as a database migration using
		# Flask-Migrate

# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.


class Show(db.Model):
	__tablename__ = 'Show'
	id = db.Column(db.Integer, primary_key=True)
	venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
	artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
	start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
		date = dateutil.parser.parse(value)
		if format == 'full':
				format = "EEEE MMMM, d, y 'at' h:mma"
		elif format == 'medium':
				format = "EE MM, dd, y h:mma"
		return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# #----------------------------------------------------------------------------#
# # Controllers.
# #----------------------------------------------------------------------------#


@app.route('/')
def index():
		return render_template('pages/home.html')


# #  Venues
# #  ----------------------------------------------------------------

@app.route('/venues')
def venues():
		# TODO: replace with real venues data.
		#       num_shows should be aggregated based on number of upcoming shows per venue.
		# data=Venues.query.all()
		data = Venue.query.order_by(Venue.city).all()
		return render_template('pages/venues.html', venues=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
		# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
		# seach for Hop should return "The Musical Hop".
		# search for "Music" should return "The Musical Hop" and "Park Square Live
		# Music & Coffee"
		# response = {
		# 		"count": 1,
		# 		"data": [{
		# 				"id": 2,
		# 				"name": "The Dueling Pianos Bar",
		# 				"num_upcoming_shows": 0,
		# 		}]
		# }
		# return render_template(
		# 		'pages/search_venues.html',
		# 		results=response,
		# 		search_term=request.form.get(
		# 				'search_term',
		# 				''))

		term = request.values.get('search_term')
		venues = Venue.query.filter(Venue.name.ilike('%' + term + '%')).all()
		response = {
			"count": len(venues),
			"data": [{"id": venue.id, "name": venue.name, "num_upcoming_shows": 0} for venue in venues]
    	}
		return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

	data = {}
	obj = Venue.query.filter_by(id=venue_id).first()
	data = {
		'id': obj.id,
		'name': obj.name,
		'genres': obj.genres,
		'address': obj.address,
		'city': obj.city,
		'state': obj.state,
		'phone': obj.phone,
		'facebook_link': obj.facebook_link,
		'seeking_talent': obj.seeking_talent,
		'image_link': obj.image_link,
		'past_shows': [
			{"artist_id":show.artist_id, "artist_name": show.name, "artist_image_link": show.image_link} 
			for show in Show.query.with_entities(Show.artist_id,  Artist.name, Artist.image_link)
			.join(Artist, Show.artist_id==Artist.id)
			.filter( Show.venue_id == venue_id)
			],
		'upcoming_shows':  [
			{"artist_id":show.artist_id, "artist_name": show.artist_name, "artist_image_link": show.artist_image_link} 
			for show in Show.query.with_entities(Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'))
			.join(Artist, Show.artist_id==Artist.id)
			.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id)
			],
		'past_shows_count': Show.query.filter( Show.venue_id == venue_id).count(),
		'upcoming_shows_count': Show.query.filter( Show.venue_id == venue_id).count()  
		}

	return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
		form = VenueForm()
		return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
# on successful db insert, flash success
# flash('Venue ' + request.form['name'] + ' was successfully listed!')
	form = VenueForm(request.form)
	if form.validate():
		try:
				new_venue = Venue(
						name=request.form['name'],
						genres=request.form.getlist('genres'),
						address=request.form['address'],
						city=request.form['city'],
						state=request.form['state'],
						phone=request.form['phone'],
						facebook_link=request.form['facebook_link'],
						image_link= request.form['image_link'],)
				db.session.add(new_venue)
				db.session.commit()
				flash('Venue ' + request.form['name'] + 'was successfully listed!')
		except SQLAlchemyError as e:
				print(e)
							# TODO: on unsuccessful db insert, flash an error instead.
							# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
							# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
				flash('An error occurred. Venue ' + \
										request.form['name'] + ' could not be listed.' + SQLAlchemyError)
	return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods = ['DELETE'])
def delete_venue(venue_id):
		# TODO: Complete this endpoint for taking a venue_id, and using
		# SQLAlchemy ORM to delete a record. Handle cases where the session commit
		# could fail.

		# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
		# clicking that button delete it from the db then redirect the user to the
		# homepage
		return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
		# TODO: replace with real data returned from querying the database
		data=Artist.query.order_by(Artist.id).all()
		return render_template('pages/artists.html', artists = data)


@app.route('/artists/search', methods = ['POST'])
def search_artists():
		# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
		# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
		# search for "band" should return "The Wild Sax Band".
		# response={
		# 		"count": 1,
		# 		"data": [{
		# 				"id": 4,
		# 				"name": "Guns N Petals",
		# 				"num_upcoming_shows": 0,
		# 		}]
		# }
		# return render_template(
		# 		'pages/search_artists.html',
		# 		results = response,
		# 		search_term = request.form.get(
		# 				'search_term',
		# 				''))
		term = request.values.get('search_term')
		artists = Artist.query.filter(Artist.name.ilike('%' + term + '%')).all()
		response = {
			"count": len(artists),
			"data": [{"id": artist.id, "name": artist.name, "num_upcoming_shows": 0} for artist in artists]
    	}
		return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 

	obj = Artist.query.filter_by(id=artist_id).first()
	data = {
		'id': obj.id,
		'name': obj.name,
		'genres': obj.genres,
		'city': obj.city,
		'state': obj.state,
		'phone': obj.phone,
		'facebook_link': obj.facebook_link,
		'seeking_description': obj.seeking_description,
		'image_link': obj.image_link,
		'past_shows': [
			{"venue_id":show.venue_id, "venue_name": show.name, "venue_image_link": show.image_link, "start_time": show.start_time.isoformat()} 
			for show in Show.query.with_entities(Show.venue_id, Show.start_time, Venue.name, Venue.image_link)
			.join(Venue, Show.venue_id==Venue.id)
			.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id)
			],
		'upcoming_shows':  [
			{"venue_id":show.venue_id, "venue_name": show.name, "venue_image_link": show.image_link, "start_time": show.start_time.isoformat()} 
			for show in Show.query.with_entities(Show.venue_id, Show.start_time, Venue.name, Venue.image_link)
			.join(Venue, Show.venue_id==Venue.id)
			.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id)
			],
		'past_shows_count': Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id).count(),
		'upcoming_shows_count': Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id).count()  
		}
	return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
		obj = Artist.query.get(artist_id)
		artist = {
			"id": obj.id,
			"name": obj.name,
			"genres": obj.genres,
			"city": obj.city,
			"state": obj.state,
			"phone": obj.phone,
			"facebook_link": obj.facebook_link,
			"seeking_venue": obj.seeking_venue,
			"seeking_description": obj.seeking_description,
			"image_link": obj.image_link
			}
		form = ArtistForm(obj=obj)
    
		return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
		# TODO: take values from the form submitted, and update existing
		# artist record with ID <artist_id> using the new attributes
	form = ArtistForm(request.form)
	artist = Artist.query.get(artist_id)
	if form.validate():
		try:
				artist = Artist(
						name=request.form['name'],
						genres=request.form.getlist('genres'),
						address=request.form['address'],
						city=request.form['city'],
						state=request.form['state'],
						phone=request.form['phone'],
						facebook_link=request.form['facebook_link'],
						image_link= request.form['image_link'],)
				db.session.add(venue_edit)
				db.session.commit()
				flash('Artist ' + request.form['name'] + 'was successfully listed!')
		except:
			db.session.rollback()
			flash("An error ocurred on edit artist")
		finally:
			db.session.close()

	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
		form = VenueForm()
		# venue = {
		# 		"id": 1,
		# 		"name": "The Musical Hop",
		# 		"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
		# 		"address": "1015 Folsom Street",
		# 		"city": "San Francisco",
		# 		"state": "CA",
		# 		"phone": "123-123-1234",
		# 		"website": "https://www.themusicalhop.com",
		# 		"facebook_link": "https://www.facebook.com/TheMusicalHop",
		# 		"seeking_talent": True,
		# 		"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
		# 		"image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
		# }
		# TODO: populate form with values from venue with ID <venue_id>
		venue = Venue.query.get(venue_id)
		return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['GET','POST'])
def edit_venue_submission(venue_id):
		# TODO: take values from the form submitted, and update existing
		# venue record with ID <venue_id> using the new attributes
	form = VenueForm(request.form)
	venue = Venue.query.get(venue_id)
	if form.validate():
		try:
				venue = Venue(
						name=request.form['name'],
						genres=request.form.getlist('genres'),
						address=request.form['address'],
						city=request.form['city'],
						state=request.form['state'],
						phone=request.form['phone'],
						facebook_link=request.form['facebook_link'],
						image_link= request.form['image_link'],)
				db.session.add(venue_edit)
				db.session.commit()
				flash('Venue ' + request.form['name'] + 'was successfully listed!')
		except SQLAlchemyError as e:
				print(e)
							# TODO: on unsuccessful db insert, flash an error instead.
							# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
							# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
				flash('An error occurred. Venue ' + \
										request.form['name'] + ' could not be listed.' + SQLAlchemyError)
	return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	form = ArtistForm(request.form)
	if form.validate():
		try:
				new_artist = Artist(
						name=request.form['name'],
						genres=request.form.getlist('genres'),
						city=request.form['city'],
						state=request.form['state'],
						phone=request.form['phone'],
						facebook_link=request.form['facebook_link'],
						image_link=request.form['image_link'])
				db.session.add(new_artist)
				db.session.commit()
				flash('Artist' + request.form['name'] + 'was successfully listed!')
		except SQLAlchemyError as e:
				print(e)
							# TODO: on unsuccessful db insert, flash an error instead.
							# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
							# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
				flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.' + SQLAlchemyError)
	return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
		# displays list of shows at /shows
		# TODO: replace with real venues data.
		# num_shows should be aggregated based on number of upcoming shows per
		# venue.
	data = []
	shows = Show.query.with_entities(
	Show.venue_id, 
	Show.artist_id, 
	Show.start_time, 
	Venue.name.label('venue_name'), 
	Artist.name.label('artist_name'), 
	Artist.image_link.label('artist_image_link')
	).join(Venue, Show.venue_id==Venue.id).join(Artist, Show.artist_id==Artist.id).all()

	for el in shows:
		data.append({
			"venue_id": el.venue_id, 
			"venue_name": el.venue_name, 
			"artist_id": el.artist_id, 
			"artist_name": el.artist_name, 
			"artist_image_link": el.artist_image_link,
		})

	return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
		# renders form. do not touch.
		form = ShowForm()
		return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	form = ShowForm(request.form)
	error = False
	try:
		show = Show(
			artist_id = request.form[artist_id.data],
			venue_id = form.venue_id.data,
			start_time = form.start_time.data
		)
		db.session.add(show)
		db.session.commit()
	except:
		error = True
		db.session.rollback()
	finally:
		db.session.close()
	if error:
		flash('An error occurred. Show could not be listed.')
	else:
		flash('Show was successfully listed!')

	return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
		return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
		return render_template('errors/500.html'), 500


if not app.debug:
		file_handler = FileHandler('error.log')
		file_handler.setFormatter(Formatter(
				'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		app.logger.setLevel(logging.INFO)
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)
		app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
		app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
		port = int(os.environ.get('PORT', 5000))
		app.run(host='0.0.0.0', port=port)
'''
