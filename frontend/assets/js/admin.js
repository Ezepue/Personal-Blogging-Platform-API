const API_BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

// Logout functionality
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
});

// Utility function for API requests
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Fetch Error: ${error.message}`);
        alert("Something went wrong. Please try again.");
        return null;
    }
}

// Load posts
async function fetchPosts() {
    const postsTable = document.querySelector("#postsTable tbody");
    postsTable.innerHTML = `<tr><td colspan="3">Loading...</td></tr>`;

    const posts = await fetchData("/articles");
    if (!posts) return;

    postsTable.innerHTML = "";
    posts.forEach(post => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${encodeURIComponent(post.title)}</td>
            <td>${encodeURIComponent(post.author)}</td>
            <td>
                <button class="edit-btn" onclick="editPost(${post.id})">Edit</button>
                <button class="delete-btn" onclick="deletePost(${post.id})">Delete</button>
            </td>
        `;
        postsTable.appendChild(row);
    });
}

// Delete post
async function deletePost(postId) {
    if (!confirm("Are you sure you want to delete this post?")) return;
    await fetchData(`/articles/${postId}`, { method: "DELETE" });
    fetchPosts();
}

// Load users
async function fetchUsers() {
    const usersTable = document.querySelector("#usersTable tbody");
    usersTable.innerHTML = `<tr><td colspan="4">Loading...</td></tr>`;

    const users = await fetchData("/users");
    if (!users) return;

    usersTable.innerHTML = "";
    users.forEach(user => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${encodeURIComponent(user.username)}</td>
            <td>${encodeURIComponent(user.email)}</td>
            <td>${encodeURIComponent(user.role)}</td>
            <td>
                <button onclick="promoteUser(${user.id})">Promote</button>
                <button class="delete-btn" onclick="deleteUser(${user.id})">Delete</button>
            </td>
        `;
        usersTable.appendChild(row);
    });
}

// Promote user
async function promoteUser(userId) {
    await fetchData(`/users/${userId}/promote`, { method: "PUT" });
    fetchUsers();
}

// Delete user
async function deleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user?")) return;
    await fetchData(`/users/${userId}`, { method: "DELETE" });
    fetchUsers();
}

// Load reported comments
async function fetchReportedComments() {
    const commentsTable = document.querySelector("#reportedCommentsTable tbody");
    commentsTable.innerHTML = `<tr><td colspan="3">Loading...</td></tr>`;

    const comments = await fetchData("/reported-comments");
    if (!comments) return;

    commentsTable.innerHTML = "";
    comments.forEach(comment => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${encodeURIComponent(comment.content)}</td>
            <td>${encodeURIComponent(comment.author)}</td>
            <td>
                <button class="delete-btn" onclick="deleteComment(${comment.id})">Delete</button>
            </td>
        `;
        commentsTable.appendChild(row);
    });
}

// Delete comment
async function deleteComment(commentId) {
    if (!confirm("Are you sure you want to delete this comment?")) return;
    await fetchData(`/comments/${commentId}`, { method: "DELETE" });
    fetchReportedComments();
}

// Load all data on page load
fetchPosts();
fetchUsers();
fetchReportedComments();
