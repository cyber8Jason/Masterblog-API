from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

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
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."}
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Get sorting parameters from URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')  # Default is ascending

    # Validate parameters
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({'error': 'Invalid sort field. Must be "title" or "content"'}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({'error': 'Invalid sort direction. Must be "asc" or "desc"'}), 400

    # Create a copy of the posts list for sorting
    sorted_posts = POSTS.copy()

    # Sort posts if a sort field is specified
    if sort_field:
        sorted_posts.sort(
            key=lambda x: x[sort_field].lower(),  # Case-insensitive sorting
            reverse=(sort_direction == 'desc')  # Reverse order for 'desc'
        )

    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def create_post():
    # Get data from request body
    data = request.get_json()

    # Create new post
    new_post = {
        'id': len(POSTS) + 1,  # Set ID to next available number
        'title': data['title'],
        'content': data['content']
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

    # Update only the fields that are present in the request
    if data.get('title') is not None:
        post_to_update['title'] = data['title']
    if data.get('content') is not None:
        post_to_update['content'] = data['content']

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get search parameters from URL
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts based on search criteria
    matching_posts = []
    for post in POSTS:
        # Check if title or content contains the search term
        if (title_query and title_query in post['title'].lower()) or \
           (content_query and content_query in post['content'].lower()):
            matching_posts.append(post)

    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
