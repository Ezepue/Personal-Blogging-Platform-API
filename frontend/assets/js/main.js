const API_BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

// 🔄 Handle authentication UI update
function updateAuthUI() {
    document.getElementById("loginLink").style.display = token ? "none" : "inline";
    document.getElementById("registerLink").style.display = token ? "none" : "inline";
    document.getElementById("logoutBtn").style.display = token ? "inline" : "none";
}


async function fetchPosts(category = "", searchQuery = "") {
    let url = `${API_BASE_URL}/articles`;
    if (category) url += `?category=${category}`;
    if (searchQuery) url += `&q=${searchQuery}`;

    try {
        const token = localStorage.getItem("access_token");
        const headers = { "Content-Type": "application/json" };

        // 🛠️ Only include the token if the user is authenticated
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(url, { method: "GET", headers });

        if (!response.ok) {
            throw new Error("Failed to fetch posts.");
        }

        const posts = await response.json();
        displayPosts(posts);
    } catch (error) {
        console.error("Error fetching posts:", error);
    }
}

// 🖥️ Display posts in UI
function displayPosts(posts) {
    const container = document.getElementById("posts-container");
    container.innerHTML = "";

    if (posts.length === 0) {
        container.innerHTML = `<p>No articles found.</p>`;  // ✅ Handle empty case
        return;
    }

    const token = localStorage.getItem("access_token");  // ✅ Get token inside function

    posts.forEach(post => {
        const postCard = document.createElement("div");
        postCard.classList.add("post-card");
        postCard.innerHTML = `
            <h3>${post.title}</h3>
            <p>${post.content.substring(0, 100)}...</p>
            <a href="post.html?id=${post.id}" class="read-more">Read More</a>
            ${token ? `<button class="edit-btn" data-id="${post.id}">Edit</button>
                       <button class="delete-btn" data-id="${post.id}">Delete</button>` : ""}
        `;
        container.appendChild(postCard);
    });

    document.querySelectorAll(".edit-btn").forEach(btn => btn.addEventListener("click", handleEdit));
    document.querySelectorAll(".delete-btn").forEach(btn => btn.addEventListener("click", handleDelete));
}

// ✏️ Edit Post
async function handleEdit(event) {
    const postId = event.target.dataset.id;
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("You must be logged in to edit posts.");
        window.location.href = "login.html";
        return;
    }

    const newTitle = prompt("Enter new title:");
    const newContent = prompt("Enter new content:");

    if (newTitle && newContent) {
        try {
            const response = await fetch(`${API_BASE_URL}/articles/${postId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ title: newTitle, content: newContent })
            });

            if (!response.ok) throw new Error("Failed to update post.");
            alert("Post updated successfully!");
            fetchPosts();  // Refresh posts
        } catch (error) {
            alert(error.message);
        }
    }
}

async function handleDelete(event) {
    const postId = event.target.dataset.id;
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("You must be logged in to delete posts.");
        window.location.href = "login.html";
        return;
    }

    if (confirm("Are you sure you want to delete this post?")) {
        try {
            const response = await fetch(`${API_BASE_URL}/articles/${postId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("Failed to delete post.");
            alert("Post deleted successfully!");
            fetchPosts();  // Refresh posts
        } catch (error) {
            alert(error.message);
        }
    }
}

// 🔍 Handle Search
document.getElementById("search-btn")?.addEventListener("click", () => {
    const query = document.getElementById("search-input").value.trim();
    fetchPosts("", query);
});

// 📂 Handle Category Filter
document.getElementById("filter-category")?.addEventListener("change", (event) => {
    fetchPosts(event.target.value);
});

// 🚀 Initialize Page
document.addEventListener("DOMContentLoaded", () => {
    updateAuthUI();
    fetchPosts();
    document.getElementById("logoutBtn")?.addEventListener("click", logout);
});
