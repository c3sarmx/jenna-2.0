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
    const error = new Error(
      data.error || "Error en la solicitud"
    );

    error.status = response.status;

    throw error;
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

export async function getAnalytics(
  businessId,
  { dateFrom, dateTo } = {}
) {
  const params = new URLSearchParams();

  if (dateFrom) {
    params.set("date_from", dateFrom);
  }

  if (dateTo) {
    params.set("date_to", dateTo);
  }

  const query = params.toString();

  return request(
    `/businesses/${businessId}/analytics${query ? `?${query}` : ""}`
  );
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

export async function updateWaiterStatus(businessId, waiterId, active) {
  return request(`/businesses/${businessId}/waiters/${waiterId}`, {
    method: "PATCH",
    body: JSON.stringify({
      active,
    }),
  });
}

export async function getBusinessSettings(businessId) {
  return request(`/businesses/${businessId}/settings`);
}

export async function updateBusinessSettings(
  businessId,
  weeklyReviewsPerWaiter
) {
  return request(
    `/businesses/${businessId}/settings`,
    {
      method: "PUT",
      body: JSON.stringify({
        weekly_reviews_per_waiter: weeklyReviewsPerWaiter,
      }),
    }
  );
}

export async function getBusinessWeeklyAnalytics(
  businessId,
  weekStart
) {
  const params = new URLSearchParams({
    week_start: weekStart,
  });

  return request(
    `/businesses/${businessId}/analytics/weekly?${params.toString()}`
  );
}

export async function getReviewEvidence(businessId) {
  return request(
    `/businesses/${businessId}/review-evidence`
  );
}

export async function createReviewEvidence(
  businessId,
  {
    reviewerName,
    rating,
    content,
    publishedAt,
    source = "manual_import",
    sourceUrl = null,
  }
) {
  return request(
    `/businesses/${businessId}/review-evidence`,
    {
      method: "POST",
      body: JSON.stringify({
        source,
        reviewer_name: reviewerName || null,
        rating: rating || null,
        content,
        published_at: publishedAt || null,
        source_url: sourceUrl || null,
      }),
    }
  );
}

export async function getReviewAttributions(businessId) {
  return request(
    `/businesses/${businessId}/review-attributions`
  );
}

export async function createReviewAttribution(
  businessId,
  {
    reviewEvidenceId,
    waiterId,
    method,
    confidence,
    reason = null,
  }
) {
  return request(
    `/businesses/${businessId}/review-attributions`,
    {
      method: "POST",
      body: JSON.stringify({
        review_evidence_id: reviewEvidenceId,
        waiter_id: waiterId,
        method,
        confidence,
        reason,
      }),
    }
  );
}
