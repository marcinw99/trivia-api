import json
import unittest
from random import randrange

from flaskr import create_app
from models import setup_db, db, Question, Category


def populate_db_with_categories(amount: int):
    for i in range(0, amount):
        category = Category(type=f'type{i}')
        category.insert()


def populate_db_with_questions(amount: int, category=1):
    for i in range(0, amount):
        question = Question(question=f'question{i}', answer=f'answer{i}',
                            category=category,
                            difficulty=randrange(5))
        question.insert()


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

    # Get Categories
    def test_get_accessories_success(self):
        populate_db_with_categories(2)

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 2)
        self.assertEqual(data['categories'][0]['id'], 1)
        self.assertEqual(data['categories'][0]['type'], 'type0')

    def test_get_accessories_failure_not_get_method(self):
        res = self.client().post('/categories')

        self.assertEqual(res.status_code, 405)

    # Get questions
    def test_get_questions_success(self):
        populate_db_with_categories(1)
        populate_db_with_questions(2)

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['questions'][0]['id'], 1)
        self.assertEqual(data['questions'][0]['question'], 'question0')

    def test_get_questions_success_no_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)

    def test_get_questions_success_paginated(self):
        populate_db_with_categories(1)
        populate_db_with_questions(15)

        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_questions'], 15)
        self.assertEqual(len(data['questions']), 5)
        self.assertEqual(data['questions'][0]['id'], 11)
        self.assertEqual(data['questions'][0]['question'], 'question10')

    def test_get_questions_success_empty_when_page_out_of_range(self):
        populate_db_with_categories(1)
        populate_db_with_questions(15)

        res = self.client().get('/questions?page=3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_questions'], 15)
        self.assertEqual(len(data['questions']), 0)

    def test_get_questions_failure_page_negative(self):
        populate_db_with_categories(1)
        populate_db_with_questions(5)

        res = self.client().get('/questions?page=-10')

        self.assertEqual(res.status_code, 400)

    # Delete Question
    def test_delete_question_success(self):
        populate_db_with_categories(1)
        populate_db_with_questions(1)

        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_question_error_not_found(self):
        res = self.client().delete('/questions/non-existing-id')

        self.assertEqual(res.status_code, 404)

    # Add Question
    def test_add_question_success(self):
        populate_db_with_categories(1)
        res = self.client().post('/questions', json={
            'question': 'question 1',
            'answer': 'answer 1',
            'category': 1,
            'difficulty': 3
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        questions = Question.query.all()

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].format()['question'], 'question 1')

    def test_add_question_failure_any_parameter_missing(self):
        populate_db_with_categories(1)
        res_no_question = self.client().post('/questions', json={
            'answer': 'answer 1',
            'category': 1,
            'difficulty': 3
        })
        res_no_answer = self.client().post('/questions', json={
            'question': 'question 1',
            'category': 1,
            'difficulty': 3
        })
        res_no_category = self.client().post('/questions', json={
            'question': 'question 1',
            'answer': 'answer 1',
            'difficulty': 3
        })
        res_no_difficulty = self.client().post('/questions', json={
            'question': 'question 1',
            'answer': 'answer 1',
            'category': 1,
        })

        status_codes = [res.status_code for res in
                        [res_no_question, res_no_answer, res_no_category,
                         res_no_difficulty]]

        self.assertEqual(all(code == 400 for code in status_codes), True)

    def test_add_question_failure_non_existing_category(self):
        res = self.client().post('/questions', json={
            'question': 'question 1',
            'answer': 'answer 1',
            'category': 5,
            'difficulty': 3
        })

        self.assertEqual(res.status_code, 400)

    # Get Questions In Category
    def test_get_questions_in_category_success(self):
        populate_db_with_categories(2)
        populate_db_with_questions(4)
        populate_db_with_questions(amount=2, category=2)

        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 4)
        self.assertEqual(data['total_questions'], 4)

    def test_get_questions_in_category_failure_category_does_not_exist(self):
        populate_db_with_categories(1)
        populate_db_with_questions(1)
        res = self.client().get('/categories/5/questions')

        self.assertEqual(res.status_code, 400)

    # Search questions
    def test_search_questions_success(self):
        populate_db_with_categories(1)
        populate_db_with_questions(3)

        res = self.client().post('/questions/search', json={
            'searchTerm': '2',
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['questions'][0]['question'], 'question2')
        self.assertEqual(data['total_questions'], 1)

    def test_search_questions_failure_no_search_term_parameter(self):
        populate_db_with_categories(1)
        populate_db_with_questions(1)

        res = self.client().post('/questions/search')

        self.assertEqual(res.status_code, 400)

    # Play Quiz
    def test_play_quiz_success_first_question(self):
        populate_db_with_categories(3)
        populate_db_with_questions(amount=3, category=3)

        res = self.client().post('/play-quiz', json={
            'previous_questions': [],
            'quiz_category': 3,
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn(data['question']['id'], [1, 2, 3])

    def test_play_quiz_success_second_question(self):
        populate_db_with_categories(3)
        populate_db_with_questions(amount=3, category=3)

        res = self.client().post('/play-quiz', json={
            'previous_questions': [1],
            'quiz_category': 3,
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn(data['question']['id'], [2, 3])

    def test_play_quiz_success_last_question(self):
        populate_db_with_categories(3)
        populate_db_with_questions(amount=3, category=3)

        res = self.client().post('/play-quiz', json={
            'previous_questions': [1, 2],
            'quiz_category': 3,
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['id'], 3)

    def test_play_quiz_success_no_questions_left(self):
        populate_db_with_categories(3)
        populate_db_with_questions(amount=3, category=3)

        res = self.client().post('/play-quiz', json={
            'previous_questions': [1, 2, 3],
            'quiz_category': 3,
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)

    def test_play_quiz_success_iterates_through_all_questions(self):
        populate_db_with_categories(2)
        populate_db_with_questions(amount=1, category=1)
        populate_db_with_questions(amount=1, category=2)

        first_call_res = self.client().post('/play-quiz', json={
            'previous_questions': [],
            'quiz_category': 0,
        })
        self.assertEqual(first_call_res.status_code, 200)

        first_call_data = json.loads(first_call_res.data)

        first_call_question_id = first_call_data['question']['id']

        second_call_res = self.client().post('/play-quiz', json={
            'previous_questions': [first_call_question_id],
            'quiz_category': 0,
        })
        self.assertEqual(second_call_res.status_code, 200)

        second_call_data = json.loads(second_call_res.data)

        second_call_question_id = second_call_data['question']['id']

        calls_question_ids = [first_call_question_id, second_call_question_id]
        calls_question_ids.sort()
        self.assertEqual(calls_question_ids, [1, 2])

    def test_play_quiz_failure_any_missing_parameters(self):
        res_no_quiz_category = self.client().post('/play-quiz', json={
            'quiz_category': 3,
        })

        self.assertEqual(res_no_quiz_category.status_code, 400)

        res_no_question = self.client().post('/play-quiz', json={
            'previous_questions': [1],
        })

        self.assertEqual(res_no_question.status_code, 400)

    def test_play_quiz_failure_no_such_category(self):
        res = self.client().post('/play-quiz', json={
            'previous_questions': [1],
            'quiz_category': 3,
        })

        self.assertEqual(res.status_code, 400)

        """
        TODO
        Write at least one test for each test for successful operation and for expected errors.
        """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
