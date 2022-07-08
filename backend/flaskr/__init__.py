from random import randrange

from flask import Flask, request, abort
from flask_cors import CORS
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_entities(entities):
    page = request.args.get('page', 1, type=int)

    if page < 0:
        abort(400)

    start = QUESTIONS_PER_PAGE * (page - 1)
    end = QUESTIONS_PER_PAGE * page

    return entities[start:end]


def format_entities(entities):
    return [entity.format() for entity in entities]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        return {
            'success': True,
            'categories': format_entities(categories),
        }

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()

        return {
            'success': True,
            'questions': format_entities(paginate_entities(questions)),
            'total_questions': len(questions),
            'categories': get_categories()['categories'],
        }

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term is None:
            abort(400)

        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')
        ).all()

        return {
            "success": True,
            "questions": paginate_entities(format_entities(questions)),
            "total_questions": len(questions),
        }

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()

        return {
            "success": True,
            "question_id": question_id,
        }

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question_content = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if None in [new_question_content, answer, category, difficulty]:
            abort(400)

        category_query = Category.query.filter(
            Category.id == category).one_or_none()
        if category_query is None:
            abort(400)

        new_question = Question(question=new_question_content, answer=answer,
                                category=category, difficulty=difficulty)
        new_question.insert()

        return {
            "success": True
        }

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_in_category(category_id):
        questions_query = Question.query.filter(
            Question.category == category_id).all()

        category_query = Category.query.filter(
            Category.id == category_id).one_or_none()
        if category_query is None:
            abort(400)

        return {
            'questions': paginate_entities(format_entities(questions_query)),
            'total_questions': len(questions_query),
            "success": True,
        }

    @app.route('/play-quiz', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if previous_questions is None or quiz_category is None:
            abort(400)

        # 0 means all questions
        if quiz_category != 0:
            category_query = Category.query.filter(
                Category.id == quiz_category).one_or_none()
            if category_query is None:
                abort(400)

        question_ids_in_selected_category_query = Question.query
        if quiz_category != 0:
            question_ids_in_selected_category_query = \
                question_ids_in_selected_category_query.filter(
                    Question.category == quiz_category)

        question_ids_in_selected_category_query_result = \
            question_ids_in_selected_category_query.with_entities(
                Question.id).all()

        ids_of_not_yet_asked_questions = [
            item for item in question_ids_in_selected_category_query_result if
            item[0] not in previous_questions
        ]

        if len(ids_of_not_yet_asked_questions) == 0:
            return {
                "success": True,
                "question": None,
            }

        next_question_id_index = randrange(0,
                                           len(ids_of_not_yet_asked_questions))

        next_question_id = ids_of_not_yet_asked_questions[
            next_question_id_index]

        next_question = Question.query.get(next_question_id)

        return {
            "success": True,
            "question": next_question.format(),
        }

    @app.errorhandler(400)
    def bad_request_handler(error):
        return ({"success": False, "error": 400,
                 "message": "bad request"}, 400)

    @app.errorhandler(404)
    def not_found_error_handler(error):
        return ({"success": False, "error": 404,
                 "message": "resource not found"}, 404)

    @app.errorhandler(405)
    def method_not_allowed_error_handler(error):
        return ({"success": False, "error": 405,
                 "message": "method not allowed"}, 405)

    @app.errorhandler(422)
    def unprocessable_handler(error):
        return ({"success": False, "error": 422,
                 "message": "unprocessable"}, 422)

    @app.errorhandler(500)
    def internal_server_error_handler(error):
        return ({"success": False, "error": 500,
                 "message": "internal server error"}, 500)

    return app
