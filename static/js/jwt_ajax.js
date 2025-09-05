/**
 * Helper: Get a cookie by name
 */
function getCookie(name) {
    const cookies = document.cookie?.split(';') || [];
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}

/**
 * Global fetch wrapper that automatically injects JWT access token
 * and handles refresh if access token expired.
 */
async function apiFetch(url, options = {}) {
    options.headers = options.headers || {};

    // Get current tokens from window or cookies
    let accessToken = window.JWT_ACCESS_TOKEN || getCookie('jwt_access_token');
    const refreshToken = window.JWT_REFRESH_TOKEN || getCookie('jwt_refresh_token');

    if (accessToken) {
        options.headers['Authorization'] = `Bearer ${accessToken}`;
    }

    let response = await fetch(url, options);

    // Handle expired access token (401)
    if (response.status === 401 && refreshToken) {
        const refreshResp = await fetch('/api/accounts/token/refresh/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh: refreshToken}),
        });

        if (refreshResp.ok) {
            const data = await refreshResp.json();
            // Update global access token
            window.JWT_ACCESS_TOKEN = data.access;
            options.headers['Authorization'] = `Bearer ${data.access}`;
            // Retry original request
            response = await fetch(url, options);
        } else {
            console.warn("Refresh token invalid or expired. User must login again.");
        }
    }

    return response;
}
