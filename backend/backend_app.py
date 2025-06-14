from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."}
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def create_post():
    # Hole die Daten aus dem Request-Body
    data = request.get_json()

    # Erstelle einen neuen Post
    new_post = {
        'id': len(POSTS) + 1,  # Setze die ID auf die nächste verfügbare Zahl
        'title': data['title'],
        'content': data['content']
    }

    # Füge den Post zur Liste hinzu
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Suche den Post mit der gegebenen ID
    post_index = None
    for index, post in enumerate(POSTS):
        if post['id'] == post_id:
            post_index = index
            break

    # Wenn kein Post gefunden wurde, gib 404 zurück
    if post_index is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Lösche den Post aus der Liste
    POSTS.pop(post_index)

    return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Suche den Post mit der gegebenen ID
    post_to_update = None
    for post in POSTS:
        if post['id'] == post_id:
            post_to_update = post
            break

    # Wenn kein Post gefunden wurde, gib 404 zurück
    if post_to_update is None:
        return jsonify({'error': f'Post with id {post_id} not found'}), 404

    # Hole die Daten aus dem Request-Body
    data = request.get_json()

    # Aktualisiere nur die Felder, die im Request vorhanden sind
    if data.get('title') is not None:
        post_to_update['title'] = data['title']
    if data.get('content') is not None:
        post_to_update['content'] = data['content']

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Hole die Suchparameter aus der URL
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filtere die Posts basierend auf den Suchkriterien
    matching_posts = []
    for post in POSTS:
        # Prüfe, ob der Titel oder Content den Suchbegriff enthält
        if (title_query and title_query in post['title'].lower()) or \
           (content_query and content_query in post['content'].lower()):
            matching_posts.append(post)

    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

