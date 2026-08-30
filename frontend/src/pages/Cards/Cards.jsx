import { useEffect, useState } from "react";
import { motion } from "motion/react";
import {
  createCard,
  getCards,
  getWaiters,
  updateCardStatus,
} from "../../services/api";
import "./Cards.css";

function Cards({ business }) {
  const [cards, setCards] = useState([]);
  const [waiters, setWaiters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedWaiter, setSelectedWaiter] = useState("");

  async function loadCards() {
    try {
      setLoading(true);
      setError(null);

      const [cardsData, waitersData] = await Promise.all([
        getCards(business.id),
        getWaiters(business.id),
      ]);

      setCards(cardsData);
      setWaiters(waitersData);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadInitialCards() {
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
          setError(requestError.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadInitialCards();

    return () => {
      cancelled = true;
    };
  }, [business.id]);

  async function handleCreateCard(event) {
    event.preventDefault();

    if (!selectedWaiter) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await createCard(
        business.id,
        Number(selectedWaiter)
      );

      setSelectedWaiter("");
      setShowCreateForm(false);

      await loadCards();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleCard(card) {
    try {
      setSaving(true);
      setError(null);

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
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="cards-page cards-state">
        <p>Cargando tarjetas...</p>
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

      {error && (
        <div className="cards-error">
          {error}
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

      <motion.section
        className="cards-list"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: {
            transition: {
              staggerChildren: 0.08,
            },
          },
        }}
      >
        {cards.length === 0 ? (
          <div className="cards-empty">
            <p>No hay tarjetas registradas.</p>

            <span>
              Crea una tarjeta para comenzar.
            </span>
          </div>
        ) : (
          cards.map((card) => (
            <motion.article
              className="card-item"
              key={card.id}
              variants={{
                hidden: {
                  opacity: 0,
                  y: 12,
                },
                visible: {
                  opacity: 1,
                  y: 0,
                },
              }}
              transition={{ duration: 0.4 }}
            >
              <div className="card-visual">
                <span className="card-logo">D</span>

                <span className="card-label">
                  Dukkah
                </span>

                <span className="card-id">
                  {card.public_id.slice(0, 12)}…
                </span>
              </div>

              <div className="card-details">
                <div>
                  <p>Mesero</p>
                  <h2>{card.waiter_name}</h2>
                </div>

                <div>
                  <p>Estado</p>

                  <div
                    className={`card-status ${
                      card.active
                        ? "card-status-active"
                        : ""
                    }`}
                  >
                    <span />
                    {card.active
                      ? "Activa"
                      : "Inactiva"}
                  </div>
                </div>
              </div>

              <button
                className="card-toggle"
                type="button"
                disabled={saving}
                onClick={() =>
                  handleToggleCard(card)
                }
              >
                {card.active
                  ? "Desactivar"
                  : "Activar"}
              </button>
            </motion.article>
          ))
        )}
      </motion.section>
    </div>
  );
}

export default Cards;
