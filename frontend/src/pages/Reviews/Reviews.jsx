import { useEffect, useMemo, useState } from "react";
import {
  createReviewAttribution,
  createReviewEvidence,
  getReviewAttributions,
  getReviewEvidence,
  getWaiters,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
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
  const [attributions, setAttributions] = useState([]);
  const [waiters, setWaiters] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);

  const [reviewerName, setReviewerName] = useState("");
  const [rating, setRating] = useState("");
  const [content, setContent] = useState("");
  const [publishedAt, setPublishedAt] = useState("");

  const [selectedWaiter, setSelectedWaiter] = useState("");
  const [confidence, setConfidence] = useState("confirmed");
  const [reason, setReason] = useState("");

  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);

  async function loadReviews() {
    try {
      setLoading(true);
      setError(null);

      const [
        reviewsData,
        attributionsData,
        waitersData,
      ] = await Promise.all([
        getReviewEvidence(business.id),
        getReviewAttributions(business.id),
        getWaiters(business.id),
      ]);

      setReviews(reviewsData);
      setAttributions(attributionsData);
      setWaiters(waitersData);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReviews();
  }, [business.id]);

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
    return new Set(
      attributions.map(
        (attribution) => attribution.review_evidence_id
      )
    );
  }, [attributions]);

  const attributedCount = attributedReviewIds.size;

  const unattributedCount =
    reviews.length - attributedCount;

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
        <p>Cargando reseñas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reviews reviews-state">
        <ErrorState
          error={error}
          onRetry={loadReviews}
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
          <strong>{reviews.length}</strong>
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

          <span>{reviews.length} registros</span>
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

                    <p>{review.content}</p>
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
