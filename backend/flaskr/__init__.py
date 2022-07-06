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
            'categories': format_entities(categories),
        }

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()

        return {
            'questions': format_entities(paginate_entities(questions)),
            'total_questions': len(questions),
            'categories': get_categories()['categories'],
        }

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()

        return {
            "success": True
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

    # Get questions in category
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

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found_error_handler(error):
        return ({"success": False, "error": 404,
                 "message": "resource not found"}, 404)

    return app
