// Event handler that runs when the window is fully loaded
window.onload = function() {
    // Set default date to today
    document.getElementById('post-date').valueAsDate = new Date();

    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to like a post
function likePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Send POST request to the like endpoint
    fetch(baseUrl + '/posts/' + postId + '/like', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Post liked:', data);
        // Update the likes display
        const likesSpan = document.getElementById('likes-' + postId);
        if (likesSpan) {
            likesSpan.textContent = data.likes;
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to add a comment to a post
function addComment(postId) {
    var baseUrl = document.getElementById('api-base-url').value;
    var commentAuthor = document.getElementById(`comment-author-${postId}`).value;
    var commentText = document.getElementById(`comment-text-${postId}`).value;

    // Validate input
    if (!commentAuthor || !commentText) {
        alert('Please enter both author and comment');
        return;
    }

    // Send POST request to add comment
    fetch(baseUrl + '/posts/' + postId + '/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            author: commentAuthor,
            text: commentText
        })
    })
    .then(response => response.json())
    .then(comment => {
        console.log('Comment added:', comment);
        // Clear input fields
        document.getElementById(`comment-author-${postId}`).value = '';
        document.getElementById(`comment-text-${postId}`).value = '';
        // Reload comments
        loadComments(postId);
    })
    .catch(error => console.error('Error:', error));
}

// Function to fetch all posts from the API and display them on the page
function loadPosts() {
    // Get the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Get sorting parameters
    var sortField = document.getElementById('sort-field').value;
    var sortDirection = document.getElementById('sort-direction').value;

    // Build the URL with sort parameters if they exist
    var url = baseUrl + '/posts';
    if (sortField) {
        url += `?sort=${sortField}&direction=${sortDirection}`;
    }

    // Send GET request to the posts endpoint
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Clear the post container
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // Create and append a new element for each post
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `
                    <div id="view-mode-${post.id}" data-title="${post.title}" data-content="${post.content}" data-author="${post.author}" data-date="${post.date}">
                        <h2>${post.title}</h2>
                        <p class="post-meta">By ${post.author} on ${post.date}</p>
                        <p>${post.content}</p>
                        <div class="post-actions-top">
                            <button onclick="toggleEditMode(${post.id})" class="edit-btn">✏️ Edit</button>
                        </div>
                        <div class="post-actions-bottom">
                            <div class="post-actions-bottom-left">
                                <button onclick="likePost(${post.id})" class="like-btn">
                                    ❤️ <span id="likes-${post.id}">${post.likes || 0}</span>
                                </button>
                                <button onclick="toggleComments(${post.id})" class="comment-btn">💬 Comments</button>
                            </div>
                            <button onclick="deletePost(${post.id})" class="delete-btn">🗑 Delete</button>
                        </div>
                    </div>
                    <div id="edit-mode-${post.id}" style="display: none;" class="edit-mode">
                        <input type="text" id="edit-title-${post.id}" placeholder="Title">
                        <input type="text" id="edit-content-${post.id}" placeholder="Content">
                        <input type="text" id="edit-author-${post.id}" placeholder="Author">
                        <input type="date" id="edit-date-${post.id}">
                        <div class="edit-actions">
                            <button onclick="updatePost(${post.id})" class="save-btn">Save</button>
                            <button onclick="toggleEditMode(${post.id})" class="cancel-btn">Cancel</button>
                        </div>
                    </div>
                    <div id="comment-section-${post.id}" class="comment-section" style="display: none;">
                        <div class="comment-form">
                            <input type="text" id="comment-author-${post.id}" placeholder="Your name">
                            <textarea id="comment-text-${post.id}" placeholder="Your comment"></textarea>
                            <button onclick="addComment(${post.id})">Add Comment</button>
                        </div>
                        <div id="comments-${post.id}" class="comments-container"></div>
                    </div>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to delete a post via API DELETE request
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Send DELETE request to the specific post endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts();  // Reload posts
    })
    .catch(error => console.error('Error:', error));
}

// Function to load comments for a post
function loadComments(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId + '/comments')
        .then(response => response.json())
        .then(comments => {
            const commentsContainer = document.getElementById(`comments-${postId}`);
            commentsContainer.innerHTML = comments.map(comment => `
                <div class="comment">
                    <p class="comment-text">${comment.text}</p>
                    <p class="comment-meta">By ${comment.author} on ${comment.date}</p>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error:', error));
}

// Function to toggle comment section visibility
function toggleComments(postId) {
    const commentSection = document.getElementById(`comment-section-${postId}`);
    if (commentSection.style.display === 'none') {
        commentSection.style.display = 'block';
        loadComments(postId);
    } else {
        commentSection.style.display = 'none';
    }
}

// Function to update a post
function updatePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;
    var title = document.getElementById(`edit-title-${postId}`).value;
    var content = document.getElementById(`edit-content-${postId}`).value;
    var author = document.getElementById(`edit-author-${postId}`).value;
    var date = document.getElementById(`edit-date-${postId}`).value;

    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: title,
            content: content,
            author: author,
            date: date
        })
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post updated:', post);
        toggleEditMode(postId);
        loadPosts();  // Reload posts to show changes
    })
    .catch(error => console.error('Error:', error));
}

// Function to toggle edit mode
function toggleEditMode(postId) {
    const viewMode = document.getElementById(`view-mode-${postId}`);
    const editMode = document.getElementById(`edit-mode-${postId}`);

    if (viewMode.style.display === 'none') {
        viewMode.style.display = 'block';
        editMode.style.display = 'none';
    } else {
        viewMode.style.display = 'none';
        editMode.style.display = 'block';
        // Pre-fill edit fields with current values
        const post = viewMode.dataset;
        document.getElementById(`edit-title-${postId}`).value = post.title;
        document.getElementById(`edit-content-${postId}`).value = post.content;
        document.getElementById(`edit-author-${postId}`).value = post.author;
        document.getElementById(`edit-date-${postId}`).value = post.date;
    }
}
