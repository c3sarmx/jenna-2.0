import { useEffect, useState } from "react";
import {
  getBusinessSettings,
  updateBusinessSettings,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
import "./Settings.css";

function Settings({ business }) {
  const [weeklyReviewsPerWaiter, setWeeklyReviewsPerWaiter] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadSettings() {
      try {
        setLoading(true);
        setError(null);

        const data = await getBusinessSettings(business.id);

        if (cancelled) {
          return;
        }

        setWeeklyReviewsPerWaiter(
          data.weekly_reviews_per_waiter == null
            ? ""
            : String(data.weekly_reviews_per_waiter)
        );
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

    loadSettings();

    return () => {
      cancelled = true;
    };
  }, [business.id]);

  function handleTargetChange(event) {
    setSaved(false);
    setActionError(null);
    setWeeklyReviewsPerWaiter(event.target.value);
  }

  async function handleSave() {
    const value = Number(weeklyReviewsPerWaiter);

    if (
      weeklyReviewsPerWaiter === "" ||
      !Number.isInteger(value) ||
      value < 0
    ) {
      setActionError(
        "La meta debe ser un número entero igual o mayor que 0."
      );
      return;
    }

    try {
      setSaving(true);
      setActionError(null);
      setSaved(false);

      const data = await updateBusinessSettings(
        business.id,
        value
      );

      setWeeklyReviewsPerWaiter(
        data.weekly_reviews_per_waiter == null
          ? ""
          : String(data.weekly_reviews_per_waiter)
      );

      setSaved(true);
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="settings settings-state">
        <p>Cargando configuración...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="settings settings-state">
        <ErrorState
          error={error}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  return (
    <div className="settings">
      <header className="settings-header">
        <div>
          <p className="eyebrow">Configuración</p>

          <h1>
            Ajusta cómo funciona <em>{business.name}.</em>
          </h1>

          <p className="settings-intro">
            Define la meta semanal de reseñas que Dukkah utilizará
            para medir el rendimiento del equipo.
          </p>
        </div>
      </header>

      <section className="settings-panel">
        <div className="settings-panel-heading">
          <div>
            <p className="panel-kicker">Rendimiento</p>
            <h2>Meta semanal</h2>
          </div>

          <span>Aplicada a cada mesero activo</span>
        </div>

        <p className="settings-description">
          Establece cuántas reseñas atribuidas esperas por mesero
          durante una semana. La misma meta se aplicará automáticamente
          a todos los meseros activos.
        </p>

        <div className="settings-target">
          <div className="settings-target-copy">
            <strong>Reseñas por mesero</strong>
            <span>
              Esta meta se utiliza para calcular el alcance semanal.
            </span>
          </div>

          <div className="settings-target-input">
            <input
              type="number"
              min="0"
              step="1"
              value={weeklyReviewsPerWaiter}
              onChange={handleTargetChange}
              disabled={saving}
              aria-label="Meta semanal de reseñas por mesero"
              placeholder="12"
            />
            <span>reseñas / semana</span>
          </div>
        </div>

        <div className="settings-actions">
          {actionError && (
            <p className="settings-action-error">
              {typeof actionError === "string"
                ? actionError
                : "No se pudieron guardar los cambios."}
            </p>
          )}

          {saved && (
            <p className="settings-saved">
              Cambios guardados.
            </p>
          )}

          <button
            type="button"
            className="settings-save-button"
            onClick={handleSave}
            disabled={saving || weeklyReviewsPerWaiter === ""}
          >
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default Settings;
