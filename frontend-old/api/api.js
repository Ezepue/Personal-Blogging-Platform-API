export const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Retrieves the authentication token from localStorage.
 * @returns {string|null} The access token, or null if not found.
 */
export function getToken() {
    return localStorage.getItem("access_token");
}

/**
 * Handles API requests with proper error handling.
 * @param {string} endpoint - The API endpoint.
 * @param {Object} options - Fetch options (method, headers, body, etc.).
 * @returns {Promise<any>} The API response JSON.
 * @throws {Error} If the request fails.
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers,
            ...options,
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(`API Error: ${response.status} - ${errorMessage}`);
        }

        return await response.json();
    } catch (error) {
        console.error("API Request Failed:", error.message);
        throw error;
    }
}

/**
 * Fetches the logged-in user's data.
 * @returns {Promise<Object>} The user data.
 */
export async function fetchUserData() {
    return apiRequest("/users/me");
}

/**
 * Fetches the like count for a given post.
 * @param {number} postId - The ID of the post.
 * @returns {Promise<Object>} The like data.
 */
export async function fetchLikes(postId) {
    return apiRequest(`/articles/${postId}/likes`);
}
