import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import Actor, Movie, app, db
from auth import AuthError, requires_auth

#----------------------------------------------------------------------------#
# Config
#----------------------------------------------------------------------------#
def create_app(test_config=None):
  # create and configure the app
  cors = CORS(app, resources={r"/api/*" : {"origins": "*"}})


  # after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
      response.headers.add(
          "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
      )
      response.headers.add(
          "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE"
      )
      return response

  #----------------------------------------------------------------------------#
  # Endpoints
  #----------------------------------------------------------------------------#

  # GET request to fetch list of all movies
  @app.route('/movies', methods=['GET'])
  def get_movies():
      # Fetch all movies
      movies = Movie.query.all()

      return jsonify({
          'success': True,
          'movies': [movie.format() for movie in movies]
      }),200


  # GET request to fetch list of all actors
  @app.route('/actors', methods=['GET'])
  def get_actors():
      # Fetch all actors
      actors = Actor.query.all()

      return jsonify({
          'success': True,
          'actors': [actor.format() for actor in actors]
      }),200


  # POST request to create a new actor
  @app.route('/add-actor', methods=['POST'])
  @requires_auth('post:add-actor')
  def create_actor(payload):
    info = request.get_json()
    print("INFO actor  ",info)
    if 'name' not in info:
      abort(422)
    if 'age' not in info:
      abort(422)
    if 'gender' not in info:
      abort(422)

    try:
      actor = Actor(name=info['name'],age=info['age'],gender=info['gender'])
      print(actor)
      actor.insert()
    except Exception:
      abort(400)
    return jsonify({
      'success': True, 
      'actor': actor.format()
      }),200


  # POST request to create a new movie
  @app.route('/add-movie', methods=['POST'])
  @requires_auth('post:add-movie')
  def create_movie(payload):
    info = request.get_json()
    print("INFO movie   ",info)
    if 'title' not in info:
      abort(422)
    if 'release' not in info:
      abort(422)

    try:
        movie = Movie(title=info['title'], release=info['release'])
        print(movie)
        movie.insert()
    except Exception:
        abort(400)
    return jsonify({
        'success': True, 
        'movie': movie.format()
        }),200


  # DELETE request to delete movies
  @app.route('/movies/<int:id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(payload,id):
    movie = Movie.query.filter(Movie.id == id).one_or_none()

    # if no actor found abort with 404 code
    if not movie:
        abort(404)
    try:
        movie.delete()
    except Exception:
        abort(400)
    return jsonify({
        'success': True, 
        'delete': id
        }), 200


  # DELETE request to delete actors
  @app.route('/actors/<int:id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(payload,id):
    actor = Actor.query.filter(Actor.id == id).one_or_none()
    print(actor)
    # if no actor found abort with 404 code
    if not actor:
        abort(404)
    try:
      actor.delete()
    except Exception:
      abort(400)
    return jsonify({
      'success': True, 
      'delete': id
      }), 200


  # PATCH request to update actors
  @app.route('/actors/<int:id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def update_actor(payload,id):
    info = request.get_json()
    actor = Actor.query.filter(Actor.id == id).one_or_none()
    print(actor)
    if not actor:
      abort(404)
    try:
      new_name = info['name']
      new_age = info['age']
      new_gender = info['gender']
      
      if new_name:
          actor.name = new_name
      if new_age:
          actor.age = new_age
      if new_gender:
          actor.gender = new_gender

      actor.update()
    except Exception:
      abort(400)

    return jsonify({
      'success': True, 
      'actor': actor.format()
      }), 200


  # PATCH request to update movie
  @app.route('/movies/<int:id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def update_movie(payload,id):
    info = request.get_json()
    movie = Movie.query.filter(Movie.id == id).one_or_none()
    print(movie)
    if not movie:
      abort(404)
    try:
      new_title = info['title']
      new_release = info['release']
      
      if new_title:
          movie.title = new_title
      if new_release:
          movie.release = new_release

      movie.update()
    except Exception:
      abort(400)

    return jsonify({
      'success': True, 
      'movie': movie.format()
      }), 200


  #----------------------------------------------------------------------------#
  # Error Handling
  #----------------------------------------------------------------------------#
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(404)
  def resource_not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(AuthError)
  def resource_not_found(error):
      return jsonify({
          "success": False,
          "error": error.status_code,
          "message": error.error['description']
      }), error.status_code

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400

  @app.errorhandler(401)
  def unauthorized(error):
      print(error)
      return jsonify({
          "success": False,
          "error": 401,
          "message": "Unauthorized"
      }), 401

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "Method Not Allowed"
      }), 405

  @app.errorhandler(500)
  def internal_server_error(error):
      print(error)
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      }), 500
  
  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)