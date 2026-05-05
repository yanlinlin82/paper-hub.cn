/**
 * API client for communicating with the Django backend.
 */

const API_BASE = '/api';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function request(method, url, data = null, options = {}) {
  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
      ...options.headers,
    },
    credentials: 'same-origin',
    ...options,
  };

  if (data && method !== 'GET') {
    config.body = JSON.stringify(data);
  }

  const fullUrl = `${API_BASE}${url}`;

  try {
    const response = await fetch(fullUrl, config);
    const contentType = response.headers.get('content-type');
    let result;

    if (contentType && contentType.includes('application/json')) {
      result = await response.json();
    } else {
      result = await response.text();
    }

    if (!response.ok) {
      const error = new Error(result.error || result || `HTTP ${response.status}`);
      error.status = response.status;
      error.data = result;
      throw error;
    }

    return result;
  } catch (error) {
    if (error.status) {
      throw error;
    }
    throw new Error('Network error: ' + error.message);
  }
}

const api = {
  get: (url, options) => request('GET', url, null, options),
  post: (url, data, options) => request('POST', url, data, options),
  put: (url, data, options) => request('PUT', url, data, options),
  patch: (url, data, options) => request('PATCH', url, data, options),
  delete: (url, options) => request('DELETE', url, null, options),

  // Auth
  login: (username, password) =>
    request('POST', '/login', { username, password }),
  logout: () => request('POST', '/logout'),

  // Group reviews
  getGroupInfo: (groupName) => request('GET', `/groups/${groupName}/`),
  getGroupReviews: (groupName, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request('GET', `/groups/${groupName}/reviews/${query ? '?' + query : ''}`);
  },
  getGroupReview: (groupName, reviewId) =>
    request('GET', `/groups/${groupName}/reviews/${reviewId}/`),
  getGroupRankings: (groupName, rankType, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const url = `/groups/${groupName}/rank/${rankType}/${query ? '?' + query : ''}`;
    return request('GET', url);
  },
  getUserReviews: (groupName, userId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request('GET', `/groups/${groupName}/users/${userId}/${query ? '?' + query : ''}`);
  },
  getJournalReviews: (groupName, journalName, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request('GET', `/groups/${groupName}/journals/${encodeURIComponent(journalName)}/${query ? '?' + query : ''}`);
  },

  // User
  getCurrentUser: () => request('GET', '/me/'),
  checkIn: (groupName, data) => request('POST', `/check-in`, { group_name: groupName, ...data }),

  // Translation
  translateTitle: (paperId, title) =>
    request('POST', '/translate-title', { paper_id: paperId, title }),
  translateAbstract: (paperId, abstract) =>
    request('POST', '/translate-abstract', { paper_id: paperId, abstract }),
};

export default api;
