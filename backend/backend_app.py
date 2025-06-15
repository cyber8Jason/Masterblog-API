from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import json
import os


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Swagger Configuration
SWAGGER_URL = '/api/docs'  # URL for Swagger UI
API_URL = '/data/masterblog.json'  # URL to Swagger definition file

# Register Swagger UI Blueprint
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# Constants
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'posts.json')


def load_posts():
    """Load posts from JSON file"""
    try:
        if not os.path.exists(POSTS_FILE):
            return {"posts": []}
        with open(POSTS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"posts": []}
    except Exception as e:
        print(f"Error loading posts: {e}")
        return {"posts": []}


def save_posts(posts_data):
    """Save posts to JSON file"""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(POSTS_FILE), exist_ok=True)
        with open(POSTS_FILE, 'w') as file:
            json.dump(posts_data, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving posts: {e}")
        return False


def search_posts(query=None):
    """Search posts by query string"""
    try:
        if not os.path.exists(POSTS_FILE):
            return {"posts": []}
        with open(POSTS_FILE, 'r') as file:
            data = json.load(file)
            if not query:
                return data

            filtered_posts = []
            query = query.lower()
            for post in data['posts']:
                if (query in post['title'].lower() or
                    query in post['content'].lower() or
                    query in post['author'].lower()):
                    filtered_posts.append(post)
            return {"posts": filtered_posts}
    except Exception as e:
        print(f"Error searching posts: {e}")
        return {"posts": []}


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))  # 5 posts per page by default

    # Get sorting parameters from URL
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    # Validate parameters
    valid_sort_fields = ['title', 'content', 'author', 'date']
    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({'error': f'Invalid sort field. Must be one of: {", ".join(valid_sort_fields)}'}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({'error': 'Invalid sort direction. Must be "asc" or "desc"'}), 400

    # Load posts from file
    posts_data = load_posts()
    sorted_posts = posts_data['posts'].copy()

    # Sort posts if a sort field is specified
    if sort_field:
        if sort_field == 'date':
            sorted_posts.sort(
                key=lambda x: datetime.strptime(x[sort_field], '%Y-%m-%d'),
                reverse=(sort_direction == 'desc')
            )
        else:
            sorted_posts.sort(
                key=lambda x: x[sort_field].lower(),
                reverse=(sort_direction == 'desc')
            )

    # Calculate pagination
    total_posts = len(sorted_posts)
    total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division

    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages

    # Get posts for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_posts = sorted_posts[start_idx:end_idx]

    return jsonify({
        'posts': current_posts,
        'pagination': {
            'total_posts': total_posts,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })


@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        # Get data from request body
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['title', 'content', 'author']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate data types
        if not isinstance(data.get('title'), str) or not isinstance(data.get('content'), str) or not isinstance(data.get('author'), str):
            return jsonify({'error': 'title, content, and author must be strings'}), 400

        # Load existing posts
        posts_data = load_posts()
        if not isinstance(posts_data, dict) or 'posts' not in posts_data:
            posts_data = {'posts': []}

        # Generate new ID (max ID + 1)
        existing_ids = [post.get('id', 0) for post in posts_data['posts']]
        new_id = max(existing_ids + [0]) + 1

        # Create new post
        new_post = {
            'id': new_id,
            'title': data['title'].strip(),
            'content': data['content'].strip(),
            'author': data['author'].strip(),
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'likes': 0,
            'comments': []
        }

        # Add post and save
        posts_data['posts'].append(new_post)
        if not save_posts(posts_data):
            return jsonify({'error': 'Failed to save post'}), 500

        return jsonify(new_post), 201

    except Exception as e:
        return jsonify({'error': f'Error creating post: {str(e)}'}), 500


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Load posts
    posts_data = load_posts()

    # Find post index
    post_index = None
    for index, post in enumerate(posts_data['posts']):
        if post['id'] == post_id:
            post_index = index
            break

    # If no post found, return 404
    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Remove post and save
    posts_data['posts'].pop(post_index)
    if not save_posts(posts_data):
        return jsonify({'error': 'Failed to delete post'}), 500

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Load posts
    posts_data = load_posts()

    # Find post
    post_to_update = None
    for post in posts_data['posts']:
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
            if field == 'date':
                try:
                    datetime.strptime(data[field], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            post_to_update[field] = data[field]

    # Save changes
    if not save_posts(posts_data):
        return jsonify({'error': 'Failed to update post'}), 500

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts_query():
    # Get search parameters from URL
    query = request.args.get('query', '')

    # Load posts from file
    posts_data = load_posts()

    # Filter posts based on search criteria
    if query:
        filtered_posts = []
        query = query.lower()
        for post in posts_data['posts']:
            if (query in post['title'].lower() or
                query in post['content'].lower() or
                query in post['author'].lower()):
                filtered_posts.append(post)
        return jsonify({"posts": filtered_posts})

    return jsonify(posts_data)


@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    # Load posts
    posts_data = load_posts()

    # Find post
    post_to_like = None
    for post in posts_data['posts']:
        if post['id'] == post_id:
            post_to_like = post
            break

    # If no post found, return 404
    if post_to_like is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Initialize likes if not present
    if 'likes' not in post_to_like:
        post_to_like['likes'] = 0

    # Increment likes
    post_to_like['likes'] += 1

    # Save changes
    if not save_posts(posts_data):
        return jsonify({'error': 'Failed to update likes'}), 500

    return jsonify({'likes': post_to_like['likes']}), 200


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    # Load posts
    posts_data = load_posts()

    # Find post
    post_to_comment = None
    for post in posts_data['posts']:
        if post['id'] == post_id:
            post_to_comment = post
            break

    # If no post found, return 404
    if post_to_comment is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Get comment data
    data = request.get_json()
    if not data or 'text' not in data or 'author' not in data:
        return jsonify({'error': 'Comment must include text and author'}), 400

    # Initialize comments list if it doesn't exist
    if 'comments' not in post_to_comment:
        post_to_comment['comments'] = []

    # Create new comment
    new_comment = {
        'id': len(post_to_comment['comments']) + 1,
        'text': data['text'],
        'author': data['author'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Add comment to post
    post_to_comment['comments'].append(new_comment)

    # Save changes
    if not save_posts(posts_data):
        return jsonify({'error': 'Failed to save comment'}), 500

    return jsonify(new_comment), 201


@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    # Load posts
    posts_data = load_posts()

    # Find post
    post = None
    for p in posts_data['posts']:
        if p['id'] == post_id:
            post = p
            break

    # If no post found, return 404
    if post is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Return comments (empty list if no comments yet)
    return jsonify(post.get('comments', []))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
