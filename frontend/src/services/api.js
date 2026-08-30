const API_BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Error en la solicitud");
  }

  return data;
}

export async function login(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

export async function getMe() {
  return request("/auth/me");
}

export async function logout() {
  return request("/auth/logout", {
    method: "POST",
  });
}

export async function getBusinesses() {
  return request("/businesses");
}

export async function getAnalytics(businessId) {
  return request(`/businesses/${businessId}/analytics`);
}

export async function getCards(businessId) {
  return request(`/businesses/${businessId}/cards`);
}

export async function getWaiters(businessId) {
  return request(`/businesses/${businessId}/waiters`);
}

export async function createWaiter(businessId, name) {
  return request(`/businesses/${businessId}/waiters`, {
    method: "POST",
    body: JSON.stringify({
      name,
    }),
  });
}

export async function createCard(businessId, waiterId) {
  return request(`/businesses/${businessId}/cards`, {
    method: "POST",
    body: JSON.stringify({
      waiter_id: waiterId,
    }),
  });
}

export async function updateCardStatus(businessId, cardId, active) {
  return request(`/businesses/${businessId}/cards/${cardId}`, {
    method: "PATCH",
    body: JSON.stringify({
      active,
    }),
  });
}
