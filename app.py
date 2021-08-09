#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for, jsonify, abort,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
import babel
from babel import dates
import dateutil
from dateutil import parser
import forms
from flask_migrate import Migrate
import datetime

import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    dateCreated = db.Column(db.DateTime)
    shows = db.relationship('Show', backref='ven', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    dateCreated = db.Column(db.DateTime)
    shows = db.relationship('Show', backref='art', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  #venueId = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  #artistId = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venueId = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artistId = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  start_time = db.Column(db.DateTime)


db.create_all()

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

#Recently added artists and venues. last 10

  venues = Venue.query.order_by(desc(Venue.dateCreated))
  artists = Artist.query.order_by(desc(Artist.dateCreated))
  data = []

  count = 0
  for venue in venues:
      venueDict = {}
      print("venuename" , venue.name)
      if count >= 10:
          break;
      venueDict["id"] = venue.id
      venueDict["name"] = venue.name
      data.append(venueDict)
      count += 1
  count = 0
  data1 = []
  for artist in artists:
      artistDict = {}
      if count >= 10:
          break;
      artistDict["id"] = artist.id
      artistDict["name"] = artist.name
      data1.append(artistDict)
      count += 1
  return render_template('pages/home.html',venues=data,artists=data1)



@app.route('/venues')
def venues():
    areas = []
    venues = Venue.query.all()
    csList = Venue.query.distinct('city','state')
    print("printing venue")

    for cs in csList:
        print(cs.city,cs.state)
        data = {}
        data['city']=cs.city
        data['state']= cs.state
        data['venues'] = []
        for venue in venues:
            print("venueid" , venue.id)
            venueDict = {}
            if cs.city == venue.city and cs.state == venue.state:
                venueDict["id"] =  venue.id
                venueDict["name"] = venue.name
                print("venuename" , venue.name)
                num_upcoming_shows = Show.query.filter_by(venueId = venue.id).count()
                venueDict["num_upcoming_shows"] = num_upcoming_shows
                data['venues'].append(venueDict)
        areas.append(data)
    print("areas",areas)

    return render_template('pages/venues.html', areas=areas);


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        artistDict = {}
        artistDict["id"] = artist.id
        artistDict["name"] = artist.name
        data.append(artistDict)
    return render_template('pages/artists.html', artists=data)


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = Show.query.all()
    data = []
    showDict = {}
    for show in shows:
        showDict = {}
        showDict["venue_id"] = show.venueId
        venue = Venue.query.get(show.venueId)
        showDict["venue_name"] = venue.name
        showDict["artist_id"] = show.artistId
        artist = Artist.query.get(show.artistId)
        showDict["artist_name"] = artist.name
        showDict["artist_image_link"] = artist.image_link
        showDict["start_time"] = str(show.start_time)
        data.append(showDict)
    return render_template('pages/shows.html', shows=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term','')
  print("search_term", search_term)

  venues = Venue.query.all()
  response = {}
  data = []
  count = 0
  for venue in venues:
      venueDict = {}

      if venue.name.lower().find(search_term.lower()) != -1:
         venueDict["id"] = venue.id
         venueDict["name"] = venue.name
         num_upcoming_shows = Show.query.filter_by(venueId=venue.id).count()
         venueDict["num_upcoming_shows"] = num_upcoming_shows
         count += 1
         data.append(venueDict)

  response["count"] = count
  response["data"] = data
  print("response",response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term','')
  print("search_term", search_term)

  artists = Artist.query.all()
  response = {}
  data = []
  count = 0
  for artist in artists:
      artistDict = {}

      if artist.name.lower().find(search_term.lower()) != -1:
         artistDict["id"] = artist.id
         artistDict["name"] = artist.name
         num_upcoming_shows = Show.query.filter_by(artistId=artist.id).count()
         artistDict["num_upcoming_shows"] = num_upcoming_shows
         count += 1
         data.append(artistDict)

  response["count"] = count
  response["data"] = data
  print("response",response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print("printing venue",venue)
  genres = []
  if venue.genres != None :
      genres = venue.genres.split(',')
  data = {}
  data["id"]= venue.id
  data["name"] = venue.name
  data["genres"]=genres
  data["address"] = venue.address
  data["city"] = venue.city
  data["state"] =  venue.state
  data["phone"] =  venue.phone
  data["website_link"] = venue.website_link
  data["facebook_link"] = venue.facebook_link
  print("seeking talent" , venue.seeking_talent)
  data["seeking_talent"] = venue.seeking_talent
  data["seeking_description"] = venue.seeking_description
  data["image_link"] = venue.image_link

  all_shows = Show.query.filter_by(venueId = venue.id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in all_shows:
      if show.start_time < datetime.datetime.now():
          past_showDict= {}
          artist  = Artist.query.get(show.artistId)
          past_showDict["artist_id"] = artist.id
          past_showDict["artist_name"] = artist.name
          past_showDict["artist_image_link"] = artist.image_link
          past_showDict["start_time"] = str(show.start_time)
          past_shows.append(past_showDict)
          past_shows_count += 1
      else:
          upcoming_showDict = {}
          artist = Artist.query.get(show.artistId)
          upcoming_showDict["artist_id"] = artist.id
          upcoming_showDict["artist_name"] = artist.name
          upcoming_showDict["artist_image_link"] = artist.image_link
          upcoming_showDict["start_time"] = str(show.start_time)
          upcoming_shows.append(upcoming_showDict)
          upcoming_shows_count += 1
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count

  print("Data is ",data)
  return render_template('pages/show_venue.html', venue=data)



@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = forms.VenueForm()
  print("In venue create get")
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      print("test ", request.form.getlist("genres"))
      genresList = request.form.getlist("genres")
      genres = ",".join(genresList)
      print("seeking talent" ,request.form.get("seeking_talent"))
      venue = Venue(
        name = request.form.get("name"),
        city = request.form.get("city"),
        state = request.form.get("state"),
        address = request.form.get("address"),
        phone = request.form.get("phone"),
        genres = genres,
        website_link = request.form.get("website_link"),
        image_link = request.form.get("image_link"),
        facebook_link = request.form.get("facebook_link"),
        seeking_talent = request.form.get("seeking_talent") == 'y',
        seeking_description = request.form.get("seeking_description"),
        dateCreated = datetime.datetime.now())


      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))




@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = forms.ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
      print("test ", request.form.getlist("genres"))
      genresList = request.form.getlist("genres")
      genres = ",".join(genresList)
      print("seeking talent" ,request.form.get("seeking_talent"))
      artist = Artist(
        name = request.form.get("name"),
        city = request.form.get("city"),
        state = request.form.get("state"),
        phone = request.form.get("phone"),
        genres = genres,
        image_link = request.form.get("image_link"),
        facebook_link = request.form.get("facebook_link"),
        seeking_venue = request.form.get("seeking_venue") == 'y',
        seeking_description = request.form.get("seeking_description"),
        dateCreated = datetime.datetime.now())

      db.session.add(artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))




@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  print("printing artist", artist)
  genres = []
  if artist.genres != None:
      genres = artist.genres.split(',')
  data = {}
  data["id"] = artist.id
  data["name"] = artist.name
  data["genres"] = genres
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website_link"] = artist.website_link
  data["facebook_link"] = artist.facebook_link
  print("seeking venue", artist.seeking_venue)
  data["seeking_venue"] = artist.seeking_venue
  data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link

  all_shows = Show.query.filter_by(artistId=artist.id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in all_shows:
      if show.start_time < datetime.datetime.now():
          past_showDict = {}
          venue = Venue.query.get(show.venueId)
          past_showDict["venue_id"] = venue.id
          past_showDict["venue_name"] = venue.name
          past_showDict["venue_image_link"] = venue.image_link
          past_showDict["start_time"] = str(show.start_time)
          past_shows.append(past_showDict)
          past_shows_count += 1
      else:
          upcoming_showDict = {}
          venue = venue.query.get(show.venueId)
          upcoming_showDict["venue_id"] = venue.id
          upcoming_showDict["venue_name"] = venue.name
          upcoming_showDict["venue_image_link"] = venue.image_link
          upcoming_showDict["start_time"] = str(show.start_time)
          upcoming_shows.append(upcoming_showDict)
          upcoming_shows_count += 1
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count

  print("Data is ", data)
  return render_template('pages/show_artist.html', artist=data)



@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = forms.ArtistForm()
  artist = Artist.query.get(artist_id)
  genres = []
  if artist.genres != None:
      genres = artist.genres.split(',')
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        print("test ", request.form.getlist("genres"))
        genresList = request.form.getlist("genres")
        genres = ",".join(genresList)
        print("seeking talent", request.form.get("seeking_talent"))

        artist.name=request.form.get("name")
        artist.city=request.form.get("city")
        artist.state=request.form.get("state")
        artist.phone=request.form.get("phone")
        artist.address=request.form.get("address")
        artist.genres=genres
        artist.image_link=request.form.get("image_link")
        artist.facebook_link=request.form.get("facebook_link")
        artist.seeking_venue=request.form.get("seeking_venue") == 'y'
        artist.seeking_description=request.form.get("seeking_description")

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    if not error:
        flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = forms.VenueForm()
  venue = Venue.query.get(venue_id)
  genres = []
  if venue.genres != None:
      genres = venue.genres.split(',')
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.genres.data = genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        print("test ", request.form.getlist("genres"))
        genresList = request.form.getlist("genres")
        genres = ",".join(genresList)
        print("seeking talent", request.form.get("seeking_talent"))

        venue.name = request.form.get("name")
        venue.city = request.form.get("city")
        venue.state = request.form.get("state")
        venue.phone = request.form.get("phone")
        venue.genres = genres
        venue.image_link = request.form.get("image_link")
        venue.facebook_link = request.form.get("facebook_link")
        venue.seeking_talent = request.form.get("seeking_talent") == 'y'
        venue.seeking_description = request.form.get("seeking_description")

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    if not error:
        flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')

    # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = forms.ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
      show = Show(artistId=request.form.get("artist_id"),
                  venueId = request.form.get("venue_id"),
                  start_time = request.form.get("start_time"))

      db.session.add(show)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if not error:
      flash('Show was successfully listed!')
  else:
      flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))


@app.route('/cssearch', methods=['POST'])
def cssearch():
#search artists and venues by city,state
  cs = request.form.get('citystate')
  csList = cs.split(",")
  csVenueList = []
  csArtistList = []
  if len(csList) == 2:
      csVenueList = Venue.query.filter_by(city=csList[0],state=csList[1])
      csArtistList = Artist.query.filter_by(city=csList[0], state=csList[1])
      return render_template('pages/cssearch.html', csVenueList=csVenueList, csArtistList=csArtistList,
                             search_term= cs)
  else:
      flash('City,State in not correct format')

  return redirect(url_for('index'))


