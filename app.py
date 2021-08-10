#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import\
    (Flask,
     render_template,
     request,
     redirect,
     url_for,
     jsonify,
     abort,
     flash)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import babel
from babel import dates
import dateutil
from dateutil import parser
from forms import ArtistForm, VenueForm, ShowForm
from flask_migrate import Migrate
import datetime
from config import DatabaseURI

import sys
from models import Venue, Artist, Show, app, db


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():

    #Recently added artists and venues. last 10 . STAND OUT SUBMISSION

    venues = Venue.query.order_by(desc(Venue.dateCreated))
    artists = Artist.query.order_by(desc(Artist.dateCreated))
    data = []

    count = 0
    for venue in venues:
        venueDict = {}
        print("venuename", venue.name)
        if count >= 10:
            break
        venueDict["id"] = venue.id
        venueDict["name"] = venue.name
        data.append(venueDict)
        count += 1
    count = 0
    data1 = []
    for artist in artists:
        artistDict = {}
        if count >= 10:
            break
        artistDict["id"] = artist.id
        artistDict["name"] = artist.name
        data1.append(artistDict)
        count += 1
    return render_template('pages/home.html', venues=data, artists=data1)


@app.route('/venues')
def venues():
    areas = []
    venues = Venue.query.all()
    csList = Venue.query.distinct('city', 'state')
    print("printing venue")

    for cs in csList:
        print(cs.city, cs.state)
        data = {}
        data['city'] = cs.city
        data['state'] = cs.state
        data['venues'] = []
        for venue in venues:
            print("venue_id", venue.id)
            venueDict = {}
            if cs.city == venue.city and cs.state == venue.state:
                venueDict["id"] = venue.id
                venueDict["name"] = venue.name
                print("venuename", venue.name)
                num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).count()
                venueDict["num_upcoming_shows"] = num_upcoming_shows
                data['venues'].append(venueDict)
        areas.append(data)
    print("areas", areas)

    return render_template('pages/venues.html', areas=areas)


@app.route('/artists')
def artists():
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

    shows = Show.query.all()
    data = []
    showDict = {}
    for show in shows:
        showDict = {}
        showDict["venue_id"] = show.venue_id
        venue = Venue.query.get(show.venue_id)
        showDict["venue_name"] = venue.name
        showDict["artist_id"] = show.artist_id
        artist = Artist.query.get(show.artist_id)
        showDict["artist_name"] = artist.name
        showDict["artist_image_link"] = artist.image_link
        showDict["start_time"] = str(show.start_time)
        data.append(showDict)
    return render_template('pages/shows.html', shows=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
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
            num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).count()
            venueDict["num_upcoming_shows"] = num_upcoming_shows
            count += 1
            data.append(venueDict)

    response["count"] = count
    response["data"] = data
    print("response", response)
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
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
            num_upcoming_shows = Show.query.filter_by(artist_id=artist.id).count()
            artistDict["num_upcoming_shows"] = num_upcoming_shows
            count += 1
            data.append(artistDict)

    response["count"] = count
    response["data"] = data
    print("response", response)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    print("printing venue", venue)
    genres = []
    if venue.genres is not None:
        genres = venue.genres.split(',')
    data = {}
    data["id"] = venue.id
    data["name"] = venue.name
    data["genres"] = genres
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone

    data["website_link"] = venue.website_link
    print("website ", venue.website_link)
    data["facebook_link"] = venue.facebook_link
    print("seeking talent", venue.seeking_talent)
    data["seeking_talent"] = venue.seeking_talent
    data["seeking_description"] = venue.seeking_description
    data["image_link"] = venue.image_link

    past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.datetime.now()).all()

    print("past_shows_query ", past_shows_query)

    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in past_shows_query:
        past_showDict = {}
        artist = Artist.query.get(show.artist_id)
        past_showDict["artist_id"] = artist.id
        past_showDict["artist_name"] = artist.name
        past_showDict["artist_image_link"] = artist.image_link
        past_showDict["start_time"] = str(show.start_time)
        past_shows.append(past_showDict)
        past_shows_count += 1

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
                       Show.start_time >= datetime.datetime.now()).all()
    print("upcoming_shows_query ", upcoming_shows_query)

    for show in upcoming_shows_query:
        upcoming_showDict = {}
        artist = Artist.query.get(show.artist_id)
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

    print("Data is ", data)
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    print("In venue create get")
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    name = ""
    try:
        print("type ", type(request.form))
        form = VenueForm(request.form)

        venue = Venue()
        form.populate_obj(venue)

        name = venue.name
        print("test ", venue.genres)
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        flash('Venue ' + name + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    # on successful db insert, flash success
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    name = ""
    try:
        print("type ", type(request.form))
        form = ArtistForm(request.form)

        artist = Artist()
        form.populate_obj(artist)

        name = artist.name
        print("test ", form.genres.data)

        print("before ", artist.genres)
        artist.genres = ",".join(artist.genres)
        print("after ", artist.genres)
        #artist.genres = genres

        #print("seeking talent", request.form.get("seeking_talent"))
        # artist = Artist(
        #    name=request.form.get("name"),
        #    city=request.form.get("city"),
        #    state=request.form.get("state"),
        #    phone=request.form.get("phone"),
        #    genres=genres,
        #    image_link=request.form.get("image_link"),
        #    facebook_link=request.form.get("facebook_link"),
        #    seeking_venue=request.form.get("seeking_venue") == 'y',
        #    seeking_description=request.form.get("seeking_description"),
        #    dateCreated=datetime.datetime.now())

        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        flash('Artist ' + name + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + name + ' could not be listed.')
    # on successful db insert, flash success
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    print("printing artist", artist.genres)
    genres = []
    if artist.genres is not None:
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

    #all_shows = Show.query.filter_by(artist_id=artist.id)

    print("in list artist", artist_id)
    past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.datetime.now()).all()

    print("past_shows_query ", past_shows_query)
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in past_shows_query:
        past_showDict = {}
        venue = Venue.query.get(show.venue_id)
        past_showDict["venue_id"] = venue.id
        past_showDict["venue_name"] = venue.name
        past_showDict["venue_image_link"] = venue.image_link
        past_showDict["start_time"] = str(show.start_time)
        past_shows.append(past_showDict)
        past_shows_count += 1

    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time >= datetime.datetime.now()).all()

    for show in upcoming_shows_query:
        upcoming_showDict = {}
        venue = venue.query.get(show.venue_id)
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
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    genres = []
    if artist.genres is not None:
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

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    name = ""
    try:
        print("type ", type(request.form))
        form = ArtistForm(request.form)

        artist = Artist.query.get(artist_id)
        form.populate_obj(artist)

        name = artist.name
        artist.genres = ",".join(artist.genres)

        print("artist " + artist.city)
        # artist = Artist.query.get(artist_id)
        # print("test ", request.form.getlist("genres"))
        # genresList = request.form.getlist("genres")
        # genres = ",".join(genresList)
        # print("seeking talent", request.form.get("seeking_talent"))

        #artist.name = request.form.get("name")
        #artist.city = request.form.get("city")
        #artist.state = request.form.get("state")
        #artist.phone = request.form.get("phone")
        #artist.address = request.form.get("address")
        #artist.genres = genres
        #artist.image_link = request.form.get("image_link")
        #artist.facebook_link = request.form.get("facebook_link")
        #artist.seeking_venue = request.form.get("seeking_venue") == 'y'
        #artist.seeking_description = request.form.get("seeking_description")

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # artist record with ID <artist_id> using the new attributes

    if not error:
        #flash('Artist ' + request.form.get('name') + ' was successfully listed!')
        flash('Artist ' + name + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    genres = []
    if venue.genres is not None:
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
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:

        print("type ", type(request.form))
        form = VenueForm(request.form)

        venue = Venue.query.get(venue_id)
        form.populate_obj(venue)

        name = venue.name
        venue.genres = ",".join(venue.genres)

        print("artist " + venue.city)

        #venue = Venue.query.get(venue_id)
        #print("test ", request.form.getlist("genres"))
        #genresList = request.form.getlist("genres")
        #genres = ",".join(genresList)
        #print("seeking talent", request.form.get("seeking_talent"))

        #venue.name = request.form.get("name")
        #venue.city = request.form.get("city")
        #venue.state = request.form.get("state")
        #venue.phone = request.form.get("phone")
        #venue.address = request.form.get("address")
        #venue.genres = genres
        #venue.image_link = request.form.get("image_link")
        #venue.facebook_link = request.form.get("facebook_link")
        #venue.seeking_talent = request.form.get("seeking_talent") == 'y'
        #venue.seeking_description = request.form.get("seeking_description")

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # venue record with ID <venue_id> using the new attributes

    if not error:
        flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')

    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        print("type ", type(request.form))
        form = ShowForm(request.form)

        show = Show()
        form.populate_obj(show)
        print("show artist and venue", show.artist_id, show.venue_id)
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
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))


@app.route('/cssearch', methods=['POST'])
def cssearch():
    #search artists and venues by city,state. STAND OUT SUBMISSION
    cs = request.form.get('citystate')
    csList = cs.split(",")
    csVenueList = []
    csArtistList = []
    if len(csList) == 2:
        csVenueList = Venue.query.filter_by(city=csList[0], state=csList[1])
        csArtistList = Artist.query.filter_by(city=csList[0], state=csList[1])
        return render_template('pages/cssearch.html',
                               csVenueList=csVenueList,
                               csArtistList=csArtistList,
                               search_term=cs)
    else:
        flash('City,State in not correct format')

    return redirect(url_for('index'))
