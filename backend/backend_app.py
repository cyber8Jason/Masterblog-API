from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Swagger Configuration
SWAGGER_URL = '/api/docs'  # URL for Swagger UI
API_URL = '/static/masterblog.json'  # URL to Swagger definition file

# Register Swagger UI Blueprint
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {
        "id": 1,
        "title": "First post",
        "content": "This is the first post.",
        "author": "John Doe",
        "date": "2023-06-14"
    },
    {
        "id": 2,
        "title": "Second post",
        "content": "This is the second post.",
        "author": "Jane Smith",
        "date": "2023-06-15"
    }
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Get sorting parameters from URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')  # Default is ascending

    # Validate parameters
    valid_sort_fields = ['title', 'content', 'author', 'date']
    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({'error': f'Invalid sort field. Must be one of: {", ".join(valid_sort_fields)}'}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({'error': 'Invalid sort direction. Must be "asc" or "desc"'}), 400

    # Create a copy of the posts list for sorting
    sorted_posts = POSTS.copy()

    # Sort posts if a sort field is specified
    if sort_field:
        # Special handling for date field
        if sort_field == 'date':
            sorted_posts.sort(
                key=lambda x: datetime.strptime(x[sort_field], '%Y-%m-%d'),
                reverse=(sort_direction == 'desc')
            )
        else:
            sorted_posts.sort(
                key=lambda x: x[sort_field].lower(),  # Case-insensitive sorting
                reverse=(sort_direction == 'desc')  # Reverse order for 'desc'
            )

    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def create_post():
    # Get data from request body
    data = request.get_json()

    # Validate required fields
    required_fields = ['title', 'content', 'author']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Create new post
    new_post = {
        'id': max(post['id'] for post in POSTS) + 1,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))  # Use current date if not provided
    }

    # Add post to list
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Find post with given ID
    post_index = None
    for index, post in enumerate(POSTS):
        if post['id'] == post_id:
            post_index = index
            break

    # If no post found, return 404
    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Delete post from list
    POSTS.pop(post_index)

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Find post with given ID
    post_to_update = None
    for post in POSTS:
        if post['id'] == post_id:
            post_to_update = post
            break

    # If no post found, return 404
    if post_to_update is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Get data from request body
    data = request.get_json()

    # Update fields that are present in the request
    updateable_fields = ['title', 'content', 'author', 'date']
    for field in updateable_fields:
        if field in data:
            # Validate date format if updating date
            if field == 'date':
                try:
                    datetime.strptime(data[field], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            post_to_update[field] = data[field]

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get search parameters from URL
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()
    author_query = request.args.get('author', '').lower()
    date_query = request.args.get('date', '')

    # Filter posts based on search criteria
    matching_posts = []
    for post in POSTS:
        if ((title_query and title_query in post['title'].lower()) or
            (content_query and content_query in post['content'].lower()) or
            (author_query and author_query in post['author'].lower()) or
            (date_query and date_query in post['date'])):
            matching_posts.append(post)

    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
