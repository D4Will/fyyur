#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
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
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Models are imported from models.py

from models import Venue, Artist, Show

# class Venue(db.Model):
#     __tablename__ = 'Venue'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website_link = db.Column(db.String(120))
#     need_talent = db.Column(db.Boolean)
#     description = db.Column(db.String(500))

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate

# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website_link = db.Column(db.String(120))
#     need_talent = db.Column(db.Boolean)
#     description = db.Column(db.String(500))
    
# class Show(db.Model):
#     __tablename__ = 'Show'
#     id = db.Column(db.Integer, primary_key=True)
#     venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
#     artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
#     time = db.Column(db.DateTime)
#     venue = db.relationship(Venue, backref = db.backref('shows'))
#     artist = db.relationship(Artist, backref = db.backref('shows'))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  cityStates = Venue.query.with_entities(Venue.state, Venue.city).group_by('city', 'state').all()
  for i in cityStates:
    venues = Venue.query.filter_by(city=i.city, state=i.state).all()
    entry = {
       "city": i.state,
       "state": i.city,
       "venues": []
    }
    for k in venues:
      entry["venues"].append({
         "id": k.id,
         "name": k.name,
         "num_upcoming_shows": len(k.shows),
      })
    data.append(entry)  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term=request.form.get('search_term', '')
  searched = Venue.query.filter(Venue.name.ilike('%' + term + '%')).all()
  response = {
     "count": len(searched),
     "data": [],
  }
  for i in searched:
     response["data"].append({
        "id": i.id,
        "name": i.name,
        "num_upcoming_shows": len(i.shows),
     })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = db.session.get(Venue, venue_id)

  now = datetime.now()
  upcoming = []
  previous = []
  for show in venue.shows:
    artist = db.session.get(Artist, show.artist_id)
    show_obj = {
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
      }
    if show.time > now:
      upcoming.append(show_obj)
    else:
      previous.append(show_obj)

  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.need_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link,
    'past_shows': previous,
    'upcoming_shows': upcoming,
    'past_shows_count': len(previous),
    'upcoming_shows_count': len(upcoming),
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
  form = request.form
  talent = False
  try:
     if form['seeking_talent'] == 'y':
       talent = True
  except:
     talent = False
  try:
    data = Venue(name=form['name'], city=form['city'], state=form['state'], address=form['address'], phone=form['phone'], image_link=form['image_link'], facebook_link=form['facebook_link'], genres=form['genres'], website_link=form['website_link'], need_talent=talent, description=form['seeking_description'])
    db.session.add(data)
    db.session.commit()
    flash('Venue ' + data.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see:http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
     venue = db.session.get(Venue, venue_id)
     db.session.delete(venue)
     db.session.commit()
  except:
     db.session.rollback()
  finally:
     db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.all()
  for artist in artists:
     data.append({
        'id': artist.id,
        'name': artist.name,
     })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form.get('search_term', '')
  searched = Artist.query.filter(Artist.name.ilike('%' + term + '%')).all()
  response = {
     "count": len(searched),
     "data": [],
  }
  for i in searched:
     response["data"].append({
        "id": i.id,
        "name": i.name,
        "num_upcoming_shows": len(i.shows),
     })
  return render_template('pages/search_artists.html', results=response, search_term=term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = db.session.get(Artist, artist_id)

  now = datetime.now()
  upcoming = []
  previous = []
  for show in artist.shows:
    venue = db.session.get(Venue, show.venue_id)
    show_obj = {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
      }
    if show.time > now:
      upcoming.append(show_obj)
    else:
      previous.append(show_obj)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.need_talent,
    "seeking_description": artist.description,
    "image_link": artist.image_link,
    'past_shows': previous,
    'upcoming_shows': upcoming,
    'past_shows_count': len(previous),
    'upcoming_shows_count': len(upcoming),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.get(Artist, artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.need_talent,
    "seeking_description": artist.description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  form = request.form
  talent = False
  try:
     if form['seeking_talent'] == 'y':
       talent = True
  except:
     talent = False
  try: 
    artist = db.session.get(Artist, artist_id)
    artist.name = form['name']
    artist.genres = form['genres']
    artist.city = form['city']
    artist.state = form['state']
    artist.phone = form['phone']
    artist.website_link = form['website_link']
    artist.facebook_link = form['facebook_link']
    artist.need_talent = talent
    artist.description = form['seeking_description']
    artist.image_link = form['image_link']
    db.session.commit()
  except:
    flash('error')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.get(Venue, venue_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.need_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = request.form
  talent = False
  try:
     if form['seeking_talent'] == 'y':
       talent = True
  except:
     talent = False
  try: 
    venue = db.session.get(Venue, venue_id)
    venue.name = form['name']
    venue.genres = form['genres']
    venue.address = form['address']
    venue.city = form['city']
    venue.state = form['state']
    venue.phone = form['phone']
    venue.website_link = form['website_link']
    venue.facebook_link = form['facebook_link']
    venue.need_talent = talent
    venue.description = form['seeking_description']
    venue.image_link = form['image_link']
    db.session.commit()
  except:    
    flash('error')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

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
  form = request.form
  talent = False
  try:
     if form['seeking_venue'] == 'y':
       talent = True
  except:
     talent = False
  try:
    data = Artist(name=form['name'], city=form['city'], state=form['state'], phone=form['phone'], image_link=form['image_link'], facebook_link=form['facebook_link'], genres=form['genres'], website_link=form['website_link'], need_talent=talent, description=form['seeking_description'])
    db.session.add(data)
    db.session.commit()
    flash('Artist ' + data.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.join(Show.venue).join(Show.artist).all()
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
  
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
  form = request.form
  try:
    data = Show(artist_id=form['artist_id'], venue_id=form['venue_id'], time=form['start_time'])
    db.session.add(data)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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
