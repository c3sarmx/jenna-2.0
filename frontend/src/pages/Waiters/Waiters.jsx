import { useEffect, useState } from "react";
import { motion } from "motion/react";
import {
  createWaiter,
  getWaiters,
} from "../../services/api";
import "./Waiters.css";

function Waiters({ business }) {
  const [waiters, setWaiters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [name, setName] = useState("");

  async function loadWaiters() {
    try {
      setLoading(true);
      setError(null);

      const data = await getWaiters(business.id);
      setWaiters(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  let cancelled = false;

  async function fetchWaiters() {
    try {
      const data = await getWaiters(business.id);

      if (!cancelled) {
        setWaiters(data);
        setLoading(false);
      }
    } catch (requestError) {
      if (!cancelled) {
        setError(requestError.message);
        setLoading(false);
      }
    }
  }

  fetchWaiters();

  return () => {
    cancelled = true;
  };
}, [business.id]);

  async function handleCreateWaiter(event) {
    event.preventDefault();

    const trimmedName = name.trim();

    if (!trimmedName) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await createWaiter(business.id, trimmedName);

      setName("");
      setShowCreateForm(false);

      await loadWaiters();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="waiters-page waiters-state">
        <p>Cargando meseros...</p>
      </div>
    );
  }

  const activeWaiters = waiters.filter(
    (waiter) => waiter.active
  ).length;

  return (
    <div className="waiters-page">
      <motion.header
        className="waiters-header"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <p className="eyebrow">Meseros</p>

          <h1>
            El equipo de <em>{business.name}.</em>
          </h1>

          <p className="waiters-intro">
            Administra las personas asociadas a tus tarjetas Dukkah.
          </p>
        </div>

        <div className="waiters-header-actions">
          <div className="waiters-summary">
            <strong>{activeWaiters}</strong>
            <span>activos</span>
          </div>

          <button
            className="waiters-create-button"
            type="button"
            onClick={() =>
              setShowCreateForm((visible) => !visible)
            }
          >
            {showCreateForm ? "Cancelar" : "Nuevo mesero"}
          </button>
        </div>
      </motion.header>

      {error && (
        <div className="waiters-error">
          {error}
        </div>
      )}

      {showCreateForm && (
        <motion.form
          className="waiters-create-form"
          onSubmit={handleCreateWaiter}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
        >
          <div>
            <p className="form-kicker">Nuevo mesero</p>

            <h2>
              Registra una persona para tu equipo.
            </h2>
          </div>

          <div className="waiters-form-row">
            <input
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="Nombre del mesero"
              disabled={saving}
              autoFocus
            />

            <button
              type="submit"
              disabled={!name.trim() || saving}
            >
              {saving ? "Agregando..." : "Agregar mesero"}
            </button>
          </div>
        </motion.form>
      )}

      <motion.section
        className="waiters-list"
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
        {waiters.length === 0 ? (
          <div className="waiters-empty">
            <p>No hay meseros registrados.</p>

            <span>
              Cuando agregues uno aparecerá aquí.
            </span>
          </div>
        ) : (
          waiters.map((waiter) => (
            <motion.article
              className="waiter-card"
              key={waiter.id}
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
              <div className="waiter-avatar">
                {waiter.name.charAt(0).toUpperCase()}
              </div>

              <div className="waiter-info">
                <h2>{waiter.name}</h2>

                <span>
                  Registrado el{" "}
                  {new Date(
                    waiter.created_at
                  ).toLocaleDateString("es-MX", {
                    day: "2-digit",
                    month: "long",
                    year: "numeric",
                  })}
                </span>
              </div>

              <div
                className={`waiter-status ${
                  waiter.active
                    ? "waiter-status-active"
                    : ""
                }`}
              >
                <span />
                {waiter.active ? "Activo" : "Inactivo"}
              </div>
            </motion.article>
          ))
        )}
      </motion.section>
    </div>
  );
}

export default Waiters;