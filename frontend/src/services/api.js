const API_BASE_URL = " http://127.0.0.1:8000";

function getStoredToken() {
    return localStorage.getItem("token");
}

function getAuthHeaders(extraHeaders = {}) {
    const token = getStoredToken();
    const headers = { "Content-Type": "application/json", ...extraHeaders };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
}

async function handleResponse(res) {
    if (res.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        window.location.replace("/login");
        throw new Error("Unauthorized");
    }
    if (!res.ok) {
        let message = "Request failed";
        const errorPayload = await res.clone().json().catch(() => null);
        if (errorPayload?.detail || errorPayload?.message) {
            message = errorPayload.detail || errorPayload.message || message;
        }
        throw new Error(message);
    }
    const data = await res.json().catch(() => null);
    return data;
}

export async function apiGet(path) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "GET",
        headers: getAuthHeaders(),
        credentials: "include",
    });
    return handleResponse(res);
}

export async function apiPost(path, body) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
        credentials: "include",
    });
    return handleResponse(res);
}

// High-level helpers (adjust to your backend as needed)
export async function getMessage() {
    return apiGet("/");
}

// Signup: expects backend to return { access_token, user: { id, name, email } }
export async function signupUser(payload) {
    const data = await apiPost("/auth/signup", payload);
    if (data?.access_token) localStorage.setItem("token", data.access_token);
    if (data?.user?.id) localStorage.setItem("userId", String(data.user.id));
    return data;
}

// Login: expects backend to return { access_token, user: { id, name, email } }
export async function loginUser(payload) {
    const data = await apiPost("/auth/login", payload);
    if (data?.access_token) localStorage.setItem("token", data.access_token);
    if (data?.user?.id) localStorage.setItem("userId", String(data.user.id));
    return data;
}

export async function createGroup(payload) {
    return apiPost("/groups/create", payload);
}

export async function joinGroup(payload) {
    return apiPost("/groups/join", payload);
}

export async function getUserGroups() {
    return apiGet("/groups/view-short");
}

export async function getGroupDetails(groupId) {
    return apiGet(`/groups/${groupId}`);
}

export async function createGroupInviteLink(groupId) {
    return apiGet(`/groups/${groupId}/create-invite`);
}

export async function createGroupExpense(groupId, payload) {
    return apiPost(`/expenses/${groupId}/create-expense`, payload);
}

export async function updateGroupExpense(groupId, payload) {
    return apiPost(`/expenses/${groupId}/edit-expense`, payload);
}

export async function deleteGroupExpense(groupId, payload) {
    return apiPost(`/expenses/${groupId}/delete-expense`, payload);
}

export function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    window.location.replace("/");
}
