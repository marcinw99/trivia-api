import json
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432',
                                                         self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = db
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        with self.app.app_context():
            # clears the db
            self.db.session.remove()
            self.db.drop_all()
        pass

    def test_get_accessories_success(self):
        category = Category(type='Science')
        category.insert()

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['id'], 1)
        self.assertEqual(data['categories'][0]['type'], 'Science')

    def test_get_accessories_failure_not_get_method(self):
        res = self.client().post('/categories')

        self.assertEqual(res.status_code, 405)

    def test_delete_question_success(self):
        category = Category(type='Science')
        category.insert()
        question = Question(
            question='question 1',
            answer='answer 1',
            category=1,
            difficulty=4,
        )
        question.insert()

        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_question_error_not_found(self):
        res = self.client().delete('/questions/non-existing-id')

        self.assertEqual(res.status_code, 404)

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
