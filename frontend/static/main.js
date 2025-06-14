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
                    <h2>${post.title}</h2>
                    <p class="post-meta">By ${post.author} on ${post.date}</p>
                    <p>${post.content}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to add a new post via API POST request
function addPost() {
    // Get input values
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date').value;

    // Send POST request to the posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: postTitle,
            content: postContent,
            author: postAuthor,
            date: postDate
        })
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post added:', post);
        // Clear input fields
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        document.getElementById('post-author').value = '';
        document.getElementById('post-date').valueAsDate = new Date();
        loadPosts();  // Reload posts
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
