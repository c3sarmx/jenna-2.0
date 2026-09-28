import { useEffect, useState } from "react";
import { motion } from "motion/react";
import {
  createWaiter,
  getAnalytics,
  getWaiters,
  updateWaiterStatus,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import "./Waiters.css";

function Waiters({ business }) {
  const [waiters, setWaiters] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadWaiters() {
      try {
        setLoading(true);
        setError(null);

        const [waitersData, analyticsData] = await Promise.all([
          getWaiters(business.id),
          getAnalytics(business.id),
        ]);

        if (!cancelled) {
          setWaiters(waitersData);
          setAnalytics(analyticsData);
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

    loadWaiters();

    return () => {
      cancelled = true;
    };
  }, [business.id, retryKey]);

  async function handleToggleWaiter(waiter) {
    try {
      setSaving(true);
      setActionError(null);

      const updatedWaiter = await updateWaiterStatus(
        business.id,
        waiter.id,
        !waiter.active
      );

      setWaiters((currentWaiters) =>
        currentWaiters.map((currentWaiter) =>
          currentWaiter.id === updatedWaiter.id
            ? {
                ...currentWaiter,
                active: updatedWaiter.active,
              }
            : currentWaiter
        )
      );
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateWaiter(event) {
    event.preventDefault();

    const trimmedName = name.trim();

    if (!trimmedName) {
      return;
    }

    try {
      setSaving(true);
      setActionError(null);

      await createWaiter(business.id, trimmedName);

      setName("");
      setShowCreateForm(false);

      setRetryKey((value) => value + 1);
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="waiters-page waiters-state">
        <LoadingState message="Cargando meseros..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="waiters-page waiters-state">
        <ErrorState
          error={error}
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  const activeWaiters = waiters.filter(
    (waiter) => waiter.active
  ).length;

  const tapsByWaiter = new Map(
    (analytics?.taps_by_waiter ?? []).map((item) => [
      item.waiter_id,
      Number(item.total_taps) || 0,
    ])
  );

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
            El equipo de <span>{business.name}.</span>
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

      {actionError && (
        <div className="waiters-error">
          {actionError.message}
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

              <span className="waiter-interactions">
                {tapsByWaiter.get(waiter.id) ?? 0} interacciones
              </span>

              <button
                className={`waiter-status ${
                  waiter.active
                    ? "waiter-status-active"
                    : ""
                }`}
                type="button"
                onClick={() => handleToggleWaiter(waiter)}
                disabled={saving}
                aria-label={
                  waiter.active
                    ? `Desactivar a ${waiter.name}`
                    : `Activar a ${waiter.name}`
                }
              >
                <span />
                {waiter.active ? "Activo" : "Inactivo"}
              </button>
            </motion.article>
          ))
        )}
      </motion.section>
    </div>
  );
}

export default Waiters;