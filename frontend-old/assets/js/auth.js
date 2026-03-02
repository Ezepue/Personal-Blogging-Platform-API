const API_BASE_URL = "http://127.0.0.1:8000";


// Utility function to show/hide error messages
function showError(message = "") {
    const errorMsg = document.getElementById("error-msg");
    if (errorMsg) {
        errorMsg.textContent = message;
        errorMsg.style.display = message ? "block" : "none";
    }
}

// Function to handle login
async function login(event) {
    event.preventDefault();
    showError(); // Reset error message

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        showError("Please enter both username and password.");
        return;
    }

    try {
        document.getElementById("loginBtn").disabled = true;

        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData.toString(),
        });

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error("Unexpected server response. Please try again.");
        }

        if (!response.ok) {
            throw new Error(data.detail || "Invalid login credentials.");
        }

        // Securely store access token in memory (frontend-only)
        sessionStorage.setItem("access_token", data.access_token);

        // Refresh token should be handled via HTTP-only cookies (backend)
        console.warn("Refresh token should be stored securely via HTTP-only cookies.");

        window.location.href = "create_post.html"; // Redirect to creat post page
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById("loginBtn").disabled = false;
    }
}

// Attach event listener for login
document.getElementById("loginForm")?.addEventListener("submit", login);
