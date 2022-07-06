# Trivia API

## Getting Started

- Base URL: This app can only be run locally and is not hosted. By default, API
  is at `http://127.0.0.1:5000`
- Authentication: not required

## Error Handling

Errors are returned as JSON objects in the following format:

```
{
    "success": false,
    "error": 400,
    "message": "bad request"
}
```

Supported error types:

- 400: bad request
- 404: resource not found
- 405: method not allowed
- 422: unprocessable

## Endpoints

#### GET /categories

- General:
    - Returns a list of all categories
- Sample: `curl http://127.0.0.1:5000/categories`

```
{
    "success": true,
    "categories": [
        {
            "id": 1,
            "type": "Science"
        },
        {
            "id": 2,
            "type": "Art"
        }
    ]
}
```

#### GET /questions

- General:
    - Returns a list of questions, total questions, and categories
    - questions are paginated by default, page size is 10 items
- Sample: `curl http://127.0.0.1:5000/questions`
- Sample with pagination: `curl http://127.0.0.1:5000/questions?page=2`

```
{
    "success": true,
    "questions": [
        {
            "id": 9,
            "question": "What boxer's original name is Cassius Clay?"
            "answer": "Muhammad Ali"
            "category": 4,
            "difficulty": 1
        },
        {
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            "answer": "Apollo 13"
            "category": 5,
            "difficulty": 4
        },
        ...
    ],
    "total_questions": 17,
    "categories": [
        {
            "id": 1,
            "type": "Science"
        },
        {
            "id": 2,
            "type": "Art"
        }
    ]
}
```

#### POST /questions/search

- General:
    - Returns a list of questions which contain the provided search term as
      substring, and total questions
    - questions are paginated by default, page size is 10 items
    - Throws error 400 if search term is not provided
-

Sample: `curl -X POST http://127.0.0.1:5000/questions/search -H 'Content-Type: application/json' -d '{"searchTerm":"what"}'
`

```
{
    "success": true,
    "questions": [
        {
            "id": 9,
            "question": "What boxer's original name is Cassius Clay?"
            "answer": "Muhammad Ali"
            "category": 4,
            "difficulty": 1
        },
        {
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            "answer": "Apollo 13"
            "category": 5,
            "difficulty": 4
        },
        ...
    ],
    "total_questions": 17,
}
```

#### DELETE /questions/<question_id>

- General:
    - Deletes a question which has the provided id
    - Returns 404 if the question does not exist
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/9`

```
{
    "success": true
}
```

#### POST /questions

- General:
    - Adds a question to the database with provided question, answer, category
      and difficulty
    - Throws error 400 if provided category does not exist or some parameter is
      missing
- Sample: `
  curl -X POST http://127.0.0.1:5000/questions -H 'Content-Type: application/json' -d '{"question":"Who discovered penicillin?", "answer": "Alexander Fleming", "category": 1, "difficulty": 3}'
  `

```
{
    "success": true
}
```

#### GET /categories/<category_id>/questions

- General:
    - Returns a paginated list of questions that belong in the specified
      category, and total questions in the category
    - Throws error 400 if provided category does not exist
- Sample: `curl http://127.0.0.1:5000/categories/3/questions`

```
{
    "success": true,
    "questions": [
        {
          "answer": "Lake Victoria", 
          "category": 3, 
          "difficulty": 2, 
          "id": 13, 
          "question": "What is the largest lake in Africa?"
        }, 
        {
          "answer": "The Palace of Versailles", 
          "category": 3, 
          "difficulty": 3, 
          "id": 14, 
          "question": "In which royal palace would you find the Hall of Mirrors?"
        }, 
        {
          "answer": "Agra", 
          "category": 3, 
          "difficulty": 2, 
          "id": 15, 
          "question": "The Taj Mahal is located in which Indian city?"
        }
    ],
    "total_questions": 3
}
```

#### POST /play-quiz

- General:
    - Returns random question from the selected category
    - Provide previous questions to avoid repeating the same questions
    - Returns `null` when there are no more questions in the category
    - Throws error 400 if specified category does not exist or some parameter is
      missing
- Sample: `
  curl -X POST http://127.0.0.1:5000/play-quiz -H 'Content-Type: application/json' -d '{"previous_questions": [13, 14], "quiz_category": 3}'
  `

```
{
    "question": {
        "answer": "Agra", 
        "category": 3, 
        "difficulty": 2, 
        "id": 15, 
        "question": "The Taj Mahal is located in which Indian city?"
    }, 
    "success": true
}

```














