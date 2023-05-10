import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import Actor, Movie, app, db

print("Enter an admin authentication token;")
verification_token='Bearer ' + input()
required_headers={'Authorization': verification_token}

class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '1234','localhost:5432', self.database_name)

        # binds the app to the current context
        with self.app.app_context():
            self.db = db
            # self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    #----------------------------------------------------------------------------#
    # Test cases
    #----------------------------------------------------------------------------#
    def test_get_actors(self):
        actor = Actor(name="Brad Pitt", age="47", gender="male")
        actor.insert()

        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_movies(self):
        movie = Movie(title="Bullet train", release="21-05-2023")
        movie.insert()

        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_new_actor(self):
        new_actor = {
            'name': "Deepika Padukone",
            'age': "35",
            'gender': "female"
        } 

        res = self.client().post('/add-actor', json=new_actor, headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['name'], new_actor['name'])
        self.assertEqual(data['actor']['age'], new_actor['age'])
        self.assertEqual(data['actor']['gender'], new_actor['gender'])

    def test_create_new_movie(self):
        new_movie = {
            'title': "Piku",
            'release': "24-12-2016"
        } 

        res = self.client().post('/add-movie', json=new_movie, headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['title'], new_movie['title'])
        self.assertEqual(data['movie']['release'], new_movie['release'])

    def test_405_if_actor_creation_not_allowed(self):
        new_actor = {
            'name': "Deepika Padukone",
            'age': "35",
            'gender': "female"
        } 
        res = self.client().post("/actors", json=new_actor,headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")
    
    def test_405_if_movie_creation_not_allowed(self):
        new_movie = {
            'title': "Piku",
            'release': "24-12-2016"
        }
        res = self.client().post("/movies", json=new_movie, headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    def test_delete_actor(self):
        res = self.client().delete("/actors/1", headers=required_headers)
        data = json.loads(res.data)

        actor = Actor.query.filter(Actor.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["delete"], 1)

    def test_delete_movie(self):
        res = self.client().delete("/movies/1", headers=required_headers)
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["delete"], 1)

    def test_should_not_allow_new_actor_missing_gender(self):
        new_actor = {
            'name': "Deepika Padukone",
            'age': "35"
        } 

        res = self.client().post('/add-movie',  json=new_actor, headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])
    
    def test_should_not_allow_new_movie_missing_release(self):
        new_movie = {
            'title': "Missing release date"
        } 

        res = self.client().post('/add-movie',  json=new_movie, headers=required_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
