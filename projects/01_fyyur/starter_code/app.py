#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
   __tablename__ = 'shows'
   id = db.Column(db.Integer, primary_key= True)
   venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
   artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
   date = db.Column(db.Date, nullable =False)

   artist = db.relationship( 'Artist' , backref = db.backref('shows', lazy = True , cascade = 'all, delete-orphan'))
   venue = db.relationship( 'Venue' , backref = db.backref('shows', lazy = True , cascade = 'all, delete-orphan'))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable =False)
    music_genres = db.Column(db.String, nullable =False)
    city = db.Column(db.String(120) , nullable =False)
    state = db.Column(db.String(120), nullable =False)
    address = db.Column(db.String(120), nullable =False)
    phone = db.Column(db.String(120), unique = True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent= db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String)
    artists = db.relationship('Artist', secondary ='shows' )
    past_shows_count = db.Column(db.Integer, default = 0)
    upcoming_shows_count = db.Column(db.Integer, default = 0)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate OK

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable =False)
    city = db.Column(db.String(120), nullable =False)
    state = db.Column(db.String(120), nullable =False)
    phone = db.Column(db.String(120), nullable =False, unique = True)
    genres = db.Column(db.String(120), nullable =False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue= db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String)
    venues = db.relationship('Venue', secondary = 'shows')
    past_shows_count = db.Column(db.Integer, default = 0)
    upcoming_shows_count = db.Column(db.Integer, default = 0)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate OK

# OK TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  set_counts()
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues_data = Venue.query.all()
  cities=[]
  flag = False

  for d in venues_data :
    city = {}
    city['city'] = d.city
    city['state']= d.state
    for c in cities:
      if city['city'] == c['city'] and city['state'] == c['state']:
        flag = True
        break
    if not flag:
      cities.append(city)
    flag = False            

  for c in cities:
    dato = {}
    dato['city'] = c['city']
    dato['state'] = c['state']
    venues_data = Venue.query.filter_by( city = c['city'] , state = c['state'])
    venues_list = []
    for d in venues_data:
      venue_dato = {}
      venue_dato['id'] = d.id
      venue_dato['name'] = d.name
      venue_dato['num_upcoming_shows'] = d.upcoming_shows_count
      venues_list.append(venue_dato)
    dato['venues'] = venues_list
    data.append(dato)  

  #data=[{
   # "city": "San Francisco",
    #"state": "CA",
    #"venues": [{
     # "id": 1,
      #"name": "The Musical Hop",
      #"num_upcoming_shows": 0,
    #}, {
     # "id": 3,
      #"name": "Park Square Live Music & Coffee",
      #"num_upcoming_shows": 1,
    #}]
  #}, {
   # "city": "New York",
    #"state": "NY",
    #"venues": [{
     # "id": 2,
     # "name": "The Dueling Pianos Bar",
    #  "num_upcoming_shows": 0,
   # }]
  #}]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # OK TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_txt = request.form.get('search_term').lower().replace(' ','')
  venues_data = Venue.query.all()
  response={}
  data = []
  count = 0
  for d in venues_data:
    dato = {}
    if d.name.lower().replace(' ','').find(search_txt) != -1:
      dato['id'] = d.id
      dato['name'] = d.name
      dato['num_upcoming_shows']= d.upcoming_shows_count
      data.append(dato) 
      count+=1
  response['count'] = count
  response['data'] = data
  
  #response={
    #"count": 1,
    #"data": [{
      #"id": 2,
     # "name": "The Dueling Pianos Bar",
    #  "num_upcoming_shows": 0,
   # }]
  #}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue_data = Venue.query.filter_by(id = venue_id).first()
  data = {}
  past_shows=[]
  upcoming_shows=[]
  data['id'] = venue_data.id
  data['name'] = venue_data.name
  data['genres'] = format_genres(venue_data.music_genres)
  data['address'] = venue_data.address
  data['city'] = venue_data.city
  data['state'] = venue_data.state
  data['phone'] = venue_data.phone
  data['website'] = venue_data.website
  data['facebook_link'] = venue_data.facebook_link
  data['seeking_talent'] = venue_data.seeking_talent
  data['seeking_description'] = venue_data.seeking_description
  data['image_link'] = venue_data.image_link
  data['past_shows_count']=venue_data.past_shows_count
  data['upcoming_shows_count'] = venue_data.upcoming_shows_count
  try:
    for a in venue_data.artists:
      shows = Show.query.filter_by(venue_id = data['id'], artist_id = a.id)
      for s in shows:
        date_now = datetime.datetime.now()
        show_date = s.date
        show = {}
        if show_date.year == date_now.year:
          if show_date.month == date_now.month:
            if show_date.day == date_now.day:
              show['artist_id'] = a.id
              show['artist_name'] = a.name
              show['artist_image_link'] = a.image_link
              show['start_time'] = str (show_date)
              upcoming_shows.append(show)
              continue
            elif show_date.day < date_now.day:
              show['artist_id'] = a.id
              show['artist_name'] = a.name
              show['artist_image_link'] = a.image_link
              show['start_time'] = str (show_date)
              past_shows.append(show) 
              continue 
          elif show_date.month < date_now.month:
            show['artist_id'] = a.id
            show['artist_name'] = a.name
            show['artist_image_link'] = a.image_link
            show['start_time'] = str (show_date)
            past_shows.append(show)
            continue
        elif show_date.year < date_now.year:
          show['artist_id'] = a.id
          show['artist_name'] = a.name
          show['artist_image_link'] = a.image_link
          show['start_time'] = str (show_date)
          past_shows.append(show)
          continue
        show['artist_id'] = a.id
        show['artist_name'] = a.name
        show['artist_image_link'] = a.image_link
        show['start_time'] = str (show_date)  
        upcoming_shows.append(show)
  except:
    flash('An error occurred. Venue shows could not be listed.')

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
    # "upcoming_shows": [{
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
     # "start_time": "2035-04-01T20:00:00.000Z"
    #}, {
      #"artist_id": 6,
      #"artist_name": "The Wild Sax Band",
      #"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
     # "start_time": "2035-04-08T20:00:00.000Z"
    #}, {
      #"artist_id": 6,
      #"artist_name": "The Wild Sax Band",
      #"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
     # "start_time": "2035-04-15T20:00:00.000Z"
    #}],
    #"past_shows_count": 1,
   # "upcoming_shows_count": 1,
  #}
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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

  seeking_talent = False
  try:
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    if request.form.get('seeking_talent') == 'y':
      seeking_talent = True
    seeking_description = request.form['seeking_description']

    venue = Venue (name = name,music_genres = genres,city = city,state = state, address = address, 
      phone = phone,image_link = image_link, facebook_link = facebook_link, website = website,
      seeking_talent = seeking_talent, seeking_description = seeking_description) 
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try : 
    shows = Show.query.filter_by(venue_id = venue_id)
    for s in shows:
      db.session.delete(s)
    v = Venue.query.get(venue_id)
    db.session.delete(v)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify(url = 'http://127.0.0.1:5000')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for a in artists:
    artist = {}
    artist['id'] = a.id
    artist['name'] = a.name
    data.append(artist)  
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_txt = request.form.get('search_term').lower().replace(' ','')
  artists_data = Artist.query.all()
  response={}
  data = []
  count = 0
  for d in artists_data:
    dato = {}
    if d.name.lower().replace(' ','').find(search_txt) != -1:
      dato['id'] = d.id
      dato['name'] = d.name
      dato['num_upcoming_shows']= d.upcoming_shows_count
      data.append(dato) 
      count+=1
  response['count'] = count
  response['data'] = data
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist_data = Artist.query.filter_by(id = artist_id).first()
  data = {}
  past_shows=[]
  upcoming_shows=[]
  data['id'] = artist_data.id
  data['name'] = artist_data.name
  data['genres'] = format_genres(artist_data.genres)
  data['city'] = artist_data.city
  data['state'] = artist_data.state
  data['phone'] = artist_data.phone
  data['website'] = artist_data.website
  data['facebook_link'] = artist_data.facebook_link
  data['seeking_venue'] = artist_data.seeking_venue
  data['seeking_description'] = artist_data.seeking_description
  data['image_link'] = artist_data.image_link
  data['past_shows_count']=artist_data.past_shows_count
  data['upcoming_shows_count'] = artist_data.upcoming_shows_count
  try:
    for v in artist_data.venues:
      shows = Show.query.filter_by(artist_id = data['id'], venue_id = v.id)
      for s in shows:
        date_now = datetime.datetime.now()
        show_date = s.date
        show = {}
        if show_date.year == date_now.year:
          if show_date.month == date_now.month:
            if show_date.day == date_now.day:
              show['venue_id'] = v.id
              show['venue_name'] = v.name
              show['venue_image_link'] = v.image_link
              show['start_time'] = str (show_date)
              upcoming_shows.append(show)
              continue
            elif show_date.day < date_now.day:
              show['venue_id'] = v.id
              show['venue_name'] = v.name
              show['venue_image_link'] = v.image_link
              show['start_time'] = str (show_date)
              past_shows.append(show) 
              continue 
          elif show_date.month < date_now.month:
            show['venue_id'] = v.id
            show['venue_name'] = v.name
            show['venue_image_link'] = v.image_link
            show['start_time'] = str (show_date)
            past_shows.append(show)
            continue
        elif show_date.year < date_now.year:
          show['venue_id'] = v.id
          show['venue_name'] = v.name
          show['venue_image_link'] = v.image_link
          show['start_time'] = str (show_date)
          past_shows.append(show)
          continue
        show['venue_id'] = v.id
        show['venue_name'] = v.name
        show['venue_image_link'] = v.image_link
        show['start_time'] = str (show_date)
        upcoming_shows.append(show)
  except:
    flash('An error occurred. Venue shows could not be listed.')
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows


  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = Artist.query.filter_by(id = artist_id).first()
  artist = {}
  artist['id'] = artist_data.id
  artist['name'] = artist_data.name
  artist['genres'] = artist_data.genres
  artist['city'] = artist_data.city
  artist['state'] = artist_data.state
  artist['phone'] = artist_data.phone
  artist['website'] = artist_data.website
  artist['facebook_link'] = artist_data.facebook_link
  artist['seeking_venue'] = artist_data.seeking_venue
  artist['seeking_description'] = artist_data.seeking_description
  artist['image_link'] = artist_data.image_link
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes 
  try:
    artist = Artist.query.get(artist_id)
    if request.form.get('seeking_venue') == 'y':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False 
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link'] 
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.filter_by(id = venue_id).first()
  venue = {}
  venue['id'] = venue_data.id
  venue['name'] = venue_data.name
  venue['genres'] = venue_data.music_genres
  venue['address'] = venue_data.address
  venue['city'] = venue_data.city
  venue['state'] = venue_data.state
  venue['phone'] = venue_data.phone
  venue['website'] = venue_data.website
  venue['facebook_link'] = venue_data.facebook_link
  venue['seeking_talent'] = venue_data.seeking_talent
  venue['seeking_description'] = venue_data.seeking_description
  venue['image_link'] = venue_data.image_link
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.music_genres = request.form.getlist('genres')
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    if request.form.get('seeking_talent') == 'y':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id = venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  seeking_venue = False
  try:
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    if request.form.get('seeking_venue') == 'y':
      seeking_venue = True
    seeking_description = request.form['seeking_description']

    artist = Artist (name = name, genres = genres,city = city, state = state, phone = phone,
      image_link = image_link, facebook_link = facebook_link, website = website,
      seeking_venue = seeking_venue, seeking_description = seeking_description) 
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues_data = Venue.query.all()
  for v in venues_data:
    for a in v.artists:
      shows_data = Show.query.filter_by(venue_id = v.id, artist_id = a.id)
      for s in shows_data:
        upcoming_show = {}
        date_now = datetime.datetime.now()
        show_date = s.date
        if show_date.year == date_now.year:
          if show_date.month == date_now.month:
            if show_date.day == date_now.day:
              upcoming_show['venue_id'] = v.id
              upcoming_show['venue_name'] = v.name
              upcoming_show['artist_id'] = a.id
              upcoming_show['artist_name'] = a.name
              upcoming_show['artist_image_link'] = a.image_link
              upcoming_show['start_time'] = str(show_date)
              data.append(upcoming_show)
              continue
            elif show_date.day < date_now.day: 
              continue 
          elif show_date.month < date_now.month:
            continue
        elif show_date.year < date_now.year:
          continue
        upcoming_show['venue_id'] = v.id
        upcoming_show['venue_name'] = v.name
        upcoming_show['artist_id'] = a.id
        upcoming_show['artist_name'] = a.name
        upcoming_show['artist_image_link'] = a.image_link
        upcoming_show['start_time'] = str (show_date)
        data.append(upcoming_show)
      

    
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    date = request.form['start_time']
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id)
    show = Show(venue_id = venue.id , artist_id = artist.id , date = date)
    venue.shows.append(show)
    db.session.commit()    
    flash('Show  was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed. ' )
  finally:
    db.session.close()  
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

def set_counts():
  venues_data = Venue.query.all()
  artists_data = Artist.query.all()
  try:
    for v in venues_data:
      past_shows_count_venue = 0
      upcoming_shows_count_venue = 0
      for a in v.artists:
        shows = Show.query.filter_by(venue_id = v.id, artist_id = a.id)
        for s in shows:
          date_now = datetime.datetime.now()
          show_date = s.date
          if show_date.year == date_now.year:
            if show_date.month == date_now.month:
              if show_date.day == date_now.day:
                upcoming_shows_count_venue+=1
                continue
              elif show_date.day < date_now.day:
                past_shows_count_venue+=1
                continue 
            elif show_date.month < date_now.month:
              past_shows_count_venue+=1
              continue
          elif show_date.year < date_now.year:
            past_shows_count_venue+=1
            continue
          upcoming_shows_count_venue+=1
      v.past_shows_count = past_shows_count_venue
      v.upcoming_shows_count = upcoming_shows_count_venue
      db.session.commit()
    for a in artists_data:
      past_shows_count = 0
      upcoming_shows_count = 0
      for s in a.shows:
        date_now = datetime.datetime.now()
        show_date = s.date
        if show_date.year == date_now.year:
          if show_date.month == date_now.month:
            if show_date.day == date_now.day:
              upcoming_shows_count+=1
              continue
            elif show_date.day < date_now.day:
              past_shows_count+=1
              continue 
          elif show_date.month < date_now.month:
            past_shows_count+=1
            continue
        elif show_date.year < date_now.year:
          past_shows_count+=1
          continue
        upcoming_shows_count+=1
      a.past_shows_count = past_shows_count
      a.upcoming_shows_count = upcoming_shows_count
      db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Venue count shows could not be set.')
  finally:
    db.session.close()
def format_genres(g):
  genres_string = ''
  for c in g:
    if(c != '{' and c != '}'):
      genres_string += c
  return (genres_string).split(',')



if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
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
