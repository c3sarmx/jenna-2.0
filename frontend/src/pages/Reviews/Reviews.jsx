import { useEffect, useMemo, useState } from "react";
import {
  createReviewAttribution,
  createReviewEvidence,
  getReviewAttributions,
  getReviewEvidencePage,
  getWaiters,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import "./Reviews.css";

function formatDate(value) {
  if (!value) {
    return "Sin fecha";
  }

  return new Intl.DateTimeFormat("es-MX", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function ReviewStars({ rating }) {
  if (!rating) {
    return <span className="review-rating-empty">Sin calificación</span>;
  }

  return (
    <span className="review-stars" aria-label={`${rating} de 5 estrellas`}>
      {"★".repeat(rating)}
      <span>{"★".repeat(5 - rating)}</span>
    </span>
  );
}

function Reviews({ business }) {
  const [reviews, setReviews] = useState([]);
  const [reviewPage, setReviewPage] = useState(1);
  const [reviewTotalPages, setReviewTotalPages] = useState(0);
  const [reviewTotal, setReviewTotal] = useState(0);
  const [reviewAttributedTotal, setReviewAttributedTotal] = useState(0);
  const [reviewUnattributedTotal, setReviewUnattributedTotal] =
    useState(0);
  const [attributions, setAttributions] = useState([]);
  const [waiters, setWaiters] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  const [showOriginalReviewId, setShowOriginalReviewId] =
    useState(null);

  const [reviewerName, setReviewerName] = useState("");
  const [rating, setRating] = useState("");
  const [content, setContent] = useState("");
  const [publishedAt, setPublishedAt] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [activeDateFilter, setActiveDateFilter] = useState("Todas");
  const [reviewSearch, setReviewSearch] = useState("");
  const [reviewSearchQuery, setReviewSearchQuery] = useState("");
  const [reviewStatus, setReviewStatus] = useState("all");

  const [selectedWaiter, setSelectedWaiter] = useState("");
  const [confidence, setConfidence] = useState("confirmed");
  const [reason, setReason] = useState("");

  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setReviewSearchQuery(reviewSearch.trim());
    }, 300);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [reviewSearch]);

  async function loadReviews(
    nextDateFrom = dateFrom,
    nextDateTo = dateTo,
    nextPage = reviewPage,
    nextSearch = reviewSearchQuery,
    nextStatus = reviewStatus,
    showLoading = true
  ) {
    try {
      if (showLoading) {
        setLoading(true);
      }
      setError(null);

      const [
        reviewsData,
        attributionsData,
        waitersData,
      ] = await Promise.all([
        getReviewEvidencePage(business.id, {
          page: nextPage,
          perPage: 20,
          search: nextSearch,
          status: nextStatus,
          dateFrom: nextDateFrom,
          dateTo: nextDateTo,
        }),
        getReviewAttributions(business.id),
        getWaiters(business.id),
      ]);

      setReviews(reviewsData.items);
      setReviewPage(reviewsData.page);
      setReviewTotalPages(reviewsData.total_pages);
      setReviewTotal(reviewsData.total);
      setReviewAttributedTotal(reviewsData.attributed_total);
      setReviewUnattributedTotal(reviewsData.unattributed_total);
      setAttributions(attributionsData);
      setWaiters(waitersData);
    } catch (requestError) {
      setError(requestError);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }

  async function handleReviewPageChange(nextPage) {
    if (
      nextPage < 1 ||
      nextPage > reviewTotalPages ||
      nextPage === reviewPage
    ) {
      return;
    }

    await loadReviews(
      dateFrom,
      dateTo,
      nextPage
    );
  }

  useEffect(() => {
    setReviewPage(1);
    loadReviews(dateFrom, dateTo, 1);
  }, [business.id]);

  useEffect(() => {
    if (reviewSearchQuery === reviewSearch.trim()) {
      loadReviews(
        dateFrom,
        dateTo,
        1,
        reviewSearchQuery,
        reviewStatus,
        false
      );
    }
  }, [reviewSearchQuery]);

  const attributionsByReview = useMemo(() => {
    const grouped = new Map();

    for (const attribution of attributions) {
      const existing = grouped.get(attribution.review_evidence_id) ?? [];
      existing.push(attribution);
      grouped.set(attribution.review_evidence_id, existing);
    }

    return grouped;
  }, [attributions]);

  const waiterById = useMemo(() => {
    return new Map(
      waiters.map((waiter) => [waiter.id, waiter])
    );
  }, [waiters]);

  const attributedReviewIds = useMemo(() => {
    const reviewIds = new Set(
      reviews.map((review) => review.id)
    );

    return new Set(
      attributions
        .filter((attribution) =>
          reviewIds.has(attribution.review_evidence_id)
        )
        .map(
          (attribution) => attribution.review_evidence_id
        )
    );
  }, [attributions, reviews]);

  const attributedCount = reviewAttributedTotal;
  const unattributedCount = reviewUnattributedTotal;

  const reviewRangeStart =
    reviewTotal === 0
      ? 0
      : (reviewPage - 1) * 20 + 1;

  const reviewRangeEnd =
    reviewTotal === 0
      ? 0
      : Math.min(reviewPage * 20, reviewTotal);

  function openAttribution(review) {
    setSelectedReview(review);
    setSelectedWaiter("");
    setConfidence("confirmed");
    setReason("");
    setActionError(null);
  }

  function closeAttribution() {
    setSelectedReview(null);
    setSelectedWaiter("");
    setConfidence("confirmed");
    setReason("");
    setActionError(null);
  }

  async function handleCreateReview(event) {
    event.preventDefault();

    if (!content.trim()) {
      setActionError("Escribe el contenido de la reseña.");
      return;
    }

    try {
      setSaving(true);
      setActionError(null);

      await createReviewEvidence(
        business.id,
        {
          reviewerName,
          rating,
          content: content.trim(),
          publishedAt: publishedAt
            ? `${publishedAt}T12:00:00`
            : null,
        }
      );

      setReviewerName("");
      setRating("");
      setContent("");
      setPublishedAt("");
      setShowCreateForm(false);

      await loadReviews();
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  async function handleAttribution(event) {
    event.preventDefault();

    if (!selectedReview || !selectedWaiter) {
      setActionError("Selecciona un mesero.");
      return;
    }

    try {
      setSaving(true);
      setActionError(null);

      await createReviewAttribution(
        business.id,
        {
          reviewEvidenceId: selectedReview.id,
          waiterId: Number(selectedWaiter),
          method: "manual",
          confidence,
          reason: reason.trim() || null,
        }
      );

      closeAttribution();
      await loadReviews();
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="reviews reviews-state">
        <LoadingState message="Cargando reseñas..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="reviews reviews-state">
        <ErrorState
          error={error}
          onRetry={() => loadReviews()}
        />
      </div>
    );
  }

  return (
    <div className="reviews">
      <header className="reviews-header">
        <div>
          <p className="eyebrow">Reseñas</p>

          <h1>
            Evidencia que se puede <em>entender.</em>
          </h1>

          <p className="reviews-intro">
            Registra reseñas, revisa su atribución y mantén
            una base verificable para la analítica del equipo.
          </p>
        </div>

        <button
          type="button"
          className="reviews-primary-button"
          onClick={() => {
            setActionError(null);
            setShowCreateForm((value) => !value);
          }}
        >
          {showCreateForm
            ? "Cerrar"
            : "Registrar reseña"}
        </button>
      </header>

      <section className="reviews-summary">
        <article>
          <span>Registradas</span>
          <strong>{reviewTotal}</strong>
        </article>

        <article>
          <span>Con atribución</span>
          <strong>{attributedCount}</strong>
        </article>

        <article>
          <span>Sin atribución</span>
          <strong>{Math.max(unattributedCount, 0)}</strong>
        </article>
      </section>

      <div className="reviews-search">
        <label htmlFor="reviews-search-input">
          Buscar reseñas
        </label>

        <input
          id="reviews-search-input"
          type="search"
          value={reviewSearch}
          onChange={(event) => setReviewSearch(event.target.value)}
          placeholder="Nombre, contenido o traducción"
          autoComplete="off"
        />
      </div>

      <div className="reviews-filters" aria-label="Filtrar reseñas por fecha">
        {[
          { label: "Todas", days: null },
          { label: "7 días", days: 7 },
          { label: "30 días", days: 30 },
          { label: "90 días", days: 90 },
        ].map((filter) => {
          const isActive = activeDateFilter === filter.label;

          return (
            <button
              key={filter.label}
              type="button"
              className={`reviews-filter ${
                isActive ? "reviews-filter-active" : ""
              }`}
              onClick={() => {
                if (filter.days === null) {
                  setDateFrom("");
                  setDateTo("");
                  setActiveDateFilter("Todas");
                  loadReviews("", "", 1, reviewSearchQuery, reviewStatus, false);
                  return;
                }

                const end = new Date();
                end.setDate(end.getDate() + 1);

                const start = new Date(end);
                start.setDate(end.getDate() - filter.days);

                const formatFilterDate = (date) =>
                  date.toISOString().slice(0, 10);

                const nextDateFrom = formatFilterDate(start);
                const nextDateTo = formatFilterDate(end);

                setDateFrom(nextDateFrom);
                setDateTo(nextDateTo);
                setActiveDateFilter(filter.label);
                loadReviews(nextDateFrom, nextDateTo, 1, reviewSearchQuery, reviewStatus, false);
              }}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      <div
        className="reviews-secondary-filters"
        aria-label="Filtrar reseñas por atribución"
      >
        {[
          { value: "all", label: "Todas" },
          { value: "attributed", label: "Atribuidas" },
          { value: "unattributed", label: "Sin atribución" },
        ].map((filter) => {
          const isActive = reviewStatus === filter.value;

          return (
            <button
              key={filter.value}
              type="button"
              className={`reviews-filter ${
                isActive ? "reviews-filter-active" : ""
              }`}
              onClick={() => {
                setReviewStatus(filter.value);
                loadReviews(
                  dateFrom,
                  dateTo,
                  1,
                  reviewSearchQuery,
                  filter.value,
                  false
                );
              }}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {showCreateForm && (
        <section className="reviews-panel">
          <div className="reviews-panel-heading">
            <div>
              <p className="panel-kicker">Nueva evidencia</p>
              <h2>Registrar reseña</h2>
            </div>

            <span>Importación manual</span>
          </div>

          <form
            className="review-create-form"
            onSubmit={handleCreateReview}
          >
            <div className="review-form-grid">
              <label>
                <span>Cliente</span>
                <input
                  value={reviewerName}
                  onChange={(event) =>
                    setReviewerName(event.target.value)
                  }
                  placeholder="Nombre del cliente"
                />
              </label>

              <label>
                <span>Calificación</span>
                <select
                  value={rating}
                  onChange={(event) =>
                    setRating(event.target.value)
                  }
                >
                  <option value="">Sin calificación</option>
                  <option value="5">5 estrellas</option>
                  <option value="4">4 estrellas</option>
                  <option value="3">3 estrellas</option>
                  <option value="2">2 estrellas</option>
                  <option value="1">1 estrella</option>
                </select>
              </label>

              <label>
                <span>Fecha de publicación</span>
                <input
                  type="date"
                  value={publishedAt}
                  onChange={(event) =>
                    setPublishedAt(event.target.value)
                  }
                />
              </label>
            </div>

            <label>
              <span>Contenido</span>
              <textarea
                value={content}
                onChange={(event) =>
                  setContent(event.target.value)
                }
                placeholder="Pega aquí el contenido de la reseña..."
                rows={5}
                required
              />
            </label>

            {actionError && (
              <p className="reviews-action-error">
                {actionError.message ?? actionError}
              </p>
            )}

            <div className="review-form-actions">
              <button
                type="submit"
                className="reviews-primary-button"
                disabled={saving}
              >
                {saving ? "Guardando..." : "Guardar reseña"}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="reviews-panel">
        <div className="reviews-panel-heading">
          <div>
            <p className="panel-kicker">Registro</p>
            <h2>Reseñas registradas</h2>
          </div>

          <span>{reviewTotal} registros</span>
        </div>

        {reviews.length === 0 ? (
          <div className="reviews-empty">
            <strong>Aún no hay reseñas registradas.</strong>
            <span>
              Registra la primera para comenzar a construir
              evidencia de atribución.
            </span>
          </div>
        ) : (
          <>
            <div className="reviews-list">
            {reviews.map((review) => {
              const reviewAttributions =
                attributionsByReview.get(review.id) ?? [];

              return (
                <article
                  className="review-row"
                  key={review.id}
                >
                  <div className="review-row-main">
                    <div className="review-row-meta">
                      <span>
                        {review.reviewer_name ||
                          "Cliente"}
                      </span>

                      <span>·</span>

                      <span>
                        {formatDate(review.published_at)}
                      </span>
                    </div>

                    <ReviewStars
                      rating={review.rating}
                    />

                    <p>
                      {review.translated_content || review.content}
                    </p>

                    {review.translated_content && (
                      <button
                        type="button"
                        className="review-original-button"
                        onClick={() =>
                          setShowOriginalReviewId((currentId) =>
                            currentId === review.id
                              ? null
                              : review.id
                          )
                        }
                      >
                        {showOriginalReviewId === review.id
                          ? "Ocultar original"
                          : "Ver original"}
                      </button>
                    )}

                    {review.translated_content &&
                      showOriginalReviewId === review.id && (
                        <p className="review-original-content">
                          {review.content}
                        </p>
                      )}
                  </div>

                  <div className="review-row-side">
                    {reviewAttributions.length > 0 ? (
                      <>
                        <span className="review-status review-status-attributed">
                          Atribuida
                        </span>

                        <div className="review-attribution-list">
                          {reviewAttributions.map(
                            (attribution) => {
                              const waiter =
                                waiterById.get(
                                  attribution.waiter_id
                                );

                              return (
                                <div
                                  className="review-attribution-item"
                                  key={attribution.id}
                                >
                                  <strong>
                                    {waiter?.name ??
                                      "Mesero"}
                                  </strong>

                                  <small>
                                    {attribution.confidence}
                                  </small>
                                </div>
                              );
                            }
                          )}
                        </div>

                        <button
                          type="button"
                          className="review-link-button"
                          onClick={() =>
                            openAttribution(review)
                          }
                        >
                          + Agregar atribución
                        </button>
                      </>
                    ) : (
                      <>
                        <span className="review-status review-status-pending">
                          Sin atribución
                        </span>

                        <button
                          type="button"
                          className="review-link-button"
                          onClick={() =>
                            openAttribution(review)
                          }
                        >
                          Atribuir
                        </button>
                      </>
                    )}
                  </div>
                </article>
              );
            })}
          </div>

          {reviewTotalPages > 1 && (
            <div className="reviews-pagination">
              <span className="reviews-pagination-summary">
                Mostrando {reviewRangeStart}–{reviewRangeEnd} de {reviewTotal}
              </span>

              <div className="reviews-pagination-controls">
                <button
                  type="button"
                  className="reviews-pagination-button"
                  onClick={() =>
                    handleReviewPageChange(reviewPage - 1)
                  }
                  disabled={reviewPage === 1}
                >
                  Anterior
                </button>

                <span className="reviews-pagination-page">
                  {reviewPage} / {reviewTotalPages}
                </span>

                <button
                  type="button"
                  className="reviews-pagination-button"
                  onClick={() =>
                    handleReviewPageChange(reviewPage + 1)
                  }
                  disabled={
                    reviewPage === reviewTotalPages
                  }
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
          </>
        )}
      </section>

      {selectedReview && (
        <div className="review-modal-backdrop">
          <section className="review-modal">
            <div className="reviews-panel-heading">
              <div>
                <p className="panel-kicker">
                  Atribución
                </p>

                <h2>
                  Asociar reseña
                </h2>
              </div>

              <button
                type="button"
                className="review-close-button"
                onClick={closeAttribution}
              >
                ×
              </button>
            </div>

            <div className="review-modal-content">
              <p>
                {selectedReview.content}
              </p>
            </div>

            <form
              className="review-attribution-form"
              onSubmit={handleAttribution}
            >
              <label>
                <span>Mesero</span>

                <select
                  value={selectedWaiter}
                  onChange={(event) =>
                    setSelectedWaiter(
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    Seleccionar mesero
                  </option>

                  {waiters
                    .filter((waiter) => {
                      if (!waiter.active) {
                        return false;
                      }

                      const alreadyAttributed =
                        attributionsByReview
                          .get(selectedReview?.id) ?? [];

                      return !alreadyAttributed.some(
                        (attribution) =>
                          attribution.waiter_id === waiter.id
                      );
                    })
                    .map((waiter) => (
                      <option
                        key={waiter.id}
                        value={waiter.id}
                      >
                        {waiter.name}
                      </option>
                    ))}
                </select>
              </label>

              <label>
                <span>Confianza</span>

                <select
                  value={confidence}
                  onChange={(event) =>
                    setConfidence(event.target.value)
                  }
                >
                  <option value="confirmed">
                    Confirmada
                  </option>
                  <option value="high">
                    Alta
                  </option>
                  <option value="medium">
                    Media
                  </option>
                  <option value="low">
                    Baja
                  </option>
                </select>
              </label>

              <label>
                <span>Razón</span>

                <textarea
                  value={reason}
                  onChange={(event) =>
                    setReason(event.target.value)
                  }
                  placeholder="¿Por qué se atribuye a este mesero?"
                  rows={3}
                />
              </label>

              {actionError && (
                <p className="reviews-action-error">
                  {actionError.message ?? actionError}
                </p>
              )}

              <div className="review-form-actions">
                <button
                  type="button"
                  className="review-secondary-button"
                  onClick={closeAttribution}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  className="reviews-primary-button"
                  disabled={saving}
                >
                  {saving
                    ? "Guardando..."
                    : "Guardar atribución"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

export default Reviews;
