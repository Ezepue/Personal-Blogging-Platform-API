const API_BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

// Logout Functionality
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
});

// 🛠️ Reusable Fetch Function with Error Handling
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error("API Request Failed:", error);
        alert(error.message);
    }
}

// 🎭 Fetch User Profile
async function fetchUserProfile() {
    const user = await apiRequest("/users/me");
    if (user) {
        document.getElementById("username").textContent = user.username;
        document.getElementById("email").textContent = user.email;
        document.getElementById("role").textContent = user.role;
    }
}

// 📝 Fetch User Posts
async function fetchUserPosts() {
    const posts = await apiRequest("/users/me/posts");
    if (posts) {
        const postsList = document.getElementById("userPostsList");
        postsList.innerHTML = "";

        posts.forEach(post => {
            const listItem = document.createElement("li");
            listItem.innerHTML = `
                <h3>${post.title}</h3>
                <p>${post.content.substring(0, 100)}...</p>
                <a href="post.html?id=${post.id}" class="read-more">Read More</a>
            `;
            postsList.appendChild(listItem);
        });
    }
}

// ✏️ Update Profile
document.getElementById("updateProfileForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const newUsername = document.getElementById("newUsername").value;
    const newEmail = document.getElementById("newEmail").value;

    const updatedUser = await apiRequest("/users/me", {
        method: "PUT",
        body: JSON.stringify({ username: newUsername, email: newEmail }),
    });

    if (updatedUser) {
        alert("Profile updated successfully!");
        fetchUserProfile();
    }
});

// 🔑 Change Password
document.getElementById("changePasswordForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const currentPassword = document.getElementById("currentPassword").value;
    const newPassword = document.getElementById("newPassword").value;

    const response = await apiRequest("/users/me/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });

    if (response) alert("Password changed successfully!");
});

// 🚨 Delete Account
document.getElementById("deleteAccountBtn").addEventListener("click", async () => {
    if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;

    const response = await apiRequest("/users/me", { method: "DELETE" });

    if (response) {
        localStorage.removeItem("access_token");
        window.location.href = "register.html";
    }
});

// 🚀 Load User Profile & Posts on Page Load
document.addEventListener("DOMContentLoaded", () => {
    fetchUserProfile();
    fetchUserPosts();
});
