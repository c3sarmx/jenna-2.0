import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  createCard,
  getCards,
  getWaiters,
  updateCardStatus,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import "./Cards.css";

function Cards({ business }) {
  const [cards, setCards] = useState([]);
  const [waiters, setWaiters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedWaiter, setSelectedWaiter] = useState("");
  const [selectedCardId, setSelectedCardId] = useState(null);
  const selectedCardIdRef = useRef(null);
  const walletTrackRef = useRef(null);
  const walletScrollTimeoutRef = useRef(null);

  function selectCard(cardId) {
    selectedCardIdRef.current = cardId;
    setSelectedCardId(cardId);
  }

  useEffect(() => {
    let cancelled = false;

    async function loadCards() {
      try {
        setLoading(true);
        setError(null);

        const [cardsData, waitersData] = await Promise.all([
          getCards(business.id),
          getWaiters(business.id),
        ]);

        if (!cancelled) {
          setCards(cardsData);
          setWaiters(waitersData);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadCards();

    return () => {
      cancelled = true;
    };
  }, [business.id, retryKey]);

  async function handleCreateCard(event) {
    event.preventDefault();

    if (!selectedWaiter) {
      return;
    }

    try {
      setSaving(true);
      setActionError(null);

      await createCard(
        business.id,
        Number(selectedWaiter)
      );

      setSelectedWaiter("");
      setShowCreateForm(false);

      setRetryKey((value) => value + 1);
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleCard(card) {
    try {
      setSaving(true);
      setActionError(null);

      const updatedCard = await updateCardStatus(
        business.id,
        card.id,
        !card.active
      );

      setCards((currentCards) =>
        currentCards.map((currentCard) =>
          currentCard.id === updatedCard.id
            ? {
                ...currentCard,
                active: updatedCard.active,
              }
            : currentCard
        )
      );
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="cards-page cards-state">
        <LoadingState message="Cargando tarjetas..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="cards-page cards-state">
        <ErrorState
          error={error}
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  const activeCards = cards.filter(
    (card) => card.active
  ).length;

  return (
    <div className="cards-page">
      <motion.header
        className="cards-header"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <p className="eyebrow">Tarjetas</p>

          <h1>
            Tus tarjetas, <em>{business.name}.</em>
          </h1>

          <p className="cards-intro">
            Administra las tarjetas asociadas a tus meseros.
          </p>
        </div>

        <div className="cards-header-actions">
          <div className="cards-summary">
            <strong>{activeCards}</strong>
            <span>activas</span>
          </div>

          <button
            className="cards-create-button"
            type="button"
            onClick={() =>
              setShowCreateForm((visible) => !visible)
            }
          >
            {showCreateForm
              ? "Cancelar"
              : "Nueva tarjeta"}
          </button>
        </div>
      </motion.header>

      {actionError && (
        <div className="cards-error">
          {actionError.message}
        </div>
      )}

      {showCreateForm && (
        <motion.form
          className="cards-create-form"
          onSubmit={handleCreateCard}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
        >
          <div>
            <p className="form-kicker">
              Nueva tarjeta
            </p>

            <h2>
              Asigna una tarjeta a un mesero.
            </h2>
          </div>

          <div className="cards-form-row">
            <select
              value={selectedWaiter}
              onChange={(event) =>
                setSelectedWaiter(event.target.value)
              }
              disabled={saving}
            >
              <option value="">
                Selecciona un mesero
              </option>

              {waiters
                .filter((waiter) => waiter.active)
                .map((waiter) => (
                  <option
                    key={waiter.id}
                    value={waiter.id}
                  >
                    {waiter.name}
                  </option>
                ))}
            </select>

            <button
              type="submit"
              disabled={!selectedWaiter || saving}
            >
              {saving ? "Creando..." : "Crear tarjeta"}
            </button>
          </div>
        </motion.form>
      )}

      {cards.length === 0 ? (
        <div className="cards-empty">
          <p>No hay tarjetas registradas.</p>

          <span>
            Crea una tarjeta para comenzar.
          </span>
        </div>
      ) : (
        <motion.section
          className="cards-wallet"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.55,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div
            className="wallet-track"
            ref={walletTrackRef}
            aria-label="Tarjetas Dukkah"
            onScroll={(event) => {
              const track = event.currentTarget;

              if (walletScrollTimeoutRef.current) {
                clearTimeout(walletScrollTimeoutRef.current);
              }

              walletScrollTimeoutRef.current = setTimeout(() => {
                const cardsInView = [
                  ...track.querySelectorAll("[data-wallet-card-id]"),
                ];

                if (!cardsInView.length) {
                  return;
                }

                const trackRect = track.getBoundingClientRect();
                const center = trackRect.left + trackRect.width / 2;

                let closestCard = null;
                let closestDistance = Infinity;

                for (const cardElement of cardsInView) {
                  const rect = cardElement.getBoundingClientRect();
                  const cardCenter = rect.left + rect.width / 2;
                  const distance = Math.abs(center - cardCenter);

                  if (distance < closestDistance) {
                    closestDistance = distance;
                    closestCard = cardElement;
                  }
                }

                const nextCardId = Number(
                  closestCard?.dataset.walletCardId
                );

                if (
                  Number.isFinite(nextCardId) &&
                  nextCardId !== selectedCardId
                ) {
                  selectCard(nextCardId);
                }
              }, 180);
            }}
          >
            {cards.map((card) => {
              const isSelected =
                card.id ===
                (selectedCardId ?? cards[0]?.id);

              return (
                <button
                  className={`wallet-card ${
                    isSelected ? "wallet-card-selected" : ""
                  }`}
                  data-wallet-card-id={card.id}
                  key={card.id}
                  type="button"
                  onClick={(event) => {
                    selectCard(card.id);

                    event.currentTarget.scrollIntoView({
                      behavior: "smooth",
                      block: "nearest",
                      inline: "center",
                    });
                  }}
                >
                  <span className="wallet-card-logo">D</span>

                  <span className="wallet-card-brand">
                    Dukkah
                  </span>

                  <span className="wallet-card-waiter">
                    {card.waiter_name}
                  </span>

                  <span className="wallet-card-id">
                    {card.public_id.slice(0, 12)}…
                  </span>
                </button>
              );
            })}
          </div>

          <div className="wallet-pagination" aria-label="Seleccionar tarjeta">
            {cards.map((card) => {
              const isSelected =
                card.id === (selectedCardId ?? cards[0]?.id);

              return (
                <button
                  key={card.id}
                  type="button"
                  className={`wallet-dot ${
                    isSelected ? "wallet-dot-active" : ""
                  }`}
                  aria-label={`Seleccionar tarjeta de ${card.waiter_name}`}
                  aria-current={isSelected ? "true" : undefined}
                  onClick={() => {
                    selectCard(card.id);

                    const cardElement = document.querySelector(
                      `[data-wallet-card-id="${card.id}"]`
                    );

                    cardElement?.scrollIntoView({
                      behavior: "smooth",
                      block: "nearest",
                      inline: "center",
                    });
                  }}
                />
              );
            })}
          </div>

          {(() => {
            const selectedCard =
              cards.find((card) => card.id === selectedCardId) ??
              cards[0];

            return (
              <AnimatePresence mode="wait" initial={false}>
                <motion.div
                  className="wallet-details"
                  key={selectedCard.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{
                    duration: 0.32,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                >
                  <div>
                    <p>Mesero</p>
                    <h2>{selectedCard.waiter_name}</h2>
                  </div>

                  <div>
                    <p>Estado</p>

                    <div
                      className={`card-status ${
                        selectedCard.active
                          ? "card-status-active"
                          : ""
                      }`}
                    >
                      <span />
                      {selectedCard.active
                        ? "Activa"
                        : "Inactiva"}
                    </div>
                  </div>

                  <button
                    className="card-toggle"
                    type="button"
                    disabled={saving}
                    onClick={() =>
                      handleToggleCard(selectedCard)
                    }
                  >
                    {selectedCard.active
                      ? "Desactivar"
                      : "Activar"}
                  </button>
                </motion.div>
              </AnimatePresence>
            );
          })()}
        </motion.section>
      )}
    </div>
  );
}

export default Cards;
