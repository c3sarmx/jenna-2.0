import { useEffect, useState } from "react";
import {
  getBusinessSettings,
  updateBusinessSettings,
  updateReviewSyncSettings,
} from "../../services/api";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import "./Settings.css";

const DEFAULT_SCHEDULE = {
  mon: { start: "08:00", end: "22:00" },
  tue: { start: "08:00", end: "22:00" },
  wed: { start: "08:00", end: "22:00" },
  thu: { start: "08:00", end: "22:00" },
  fri: { start: "08:00", end: "23:00" },
  sat: { start: "08:00", end: "23:00" },
  sun: { start: "08:00", end: "20:00" },
};

const DAYS = [
  ["mon", "Lunes"],
  ["tue", "Martes"],
  ["wed", "Miércoles"],
  ["thu", "Jueves"],
  ["fri", "Viernes"],
  ["sat", "Sábado"],
  ["sun", "Domingo"],
];

function Settings({ business }) {
  const [weeklyReviewsPerWaiter, setWeeklyReviewsPerWaiter] = useState("");

  const [reviewSyncEnabled, setReviewSyncEnabled] = useState(true);
  const [reviewSyncInterval, setReviewSyncInterval] = useState("5");
  const [reviewSyncTimezone, setReviewSyncTimezone] = useState(
    "America/Mexico_City"
  );
  const [reviewSyncSchedule, setReviewSyncSchedule] = useState(
    DEFAULT_SCHEDULE
  );

  const [reviewSyncLastRunAt, setReviewSyncLastRunAt] = useState(null);
  const [reviewSyncLastErrorAt, setReviewSyncLastErrorAt] = useState(null);
  const [reviewSyncLastError, setReviewSyncLastError] = useState(null);
  const [reviewSyncConsecutiveFailures, setReviewSyncConsecutiveFailures] =
    useState(0);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingSync, setSavingSync] = useState(false);

  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [syncError, setSyncError] = useState(null);

  const [saved, setSaved] = useState(false);
  const [syncSaved, setSyncSaved] = useState(false);

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

        if (data.review_sync) {
          setReviewSyncEnabled(Boolean(data.review_sync.enabled));

          setReviewSyncInterval(
            data.review_sync.interval_minutes == null
              ? "5"
              : String(data.review_sync.interval_minutes)
          );

          setReviewSyncTimezone(
            data.review_sync.timezone || "America/Mexico_City"
          );

          setReviewSyncSchedule({
            ...DEFAULT_SCHEDULE,
            ...(data.review_sync.schedule || {}),
          });

          setReviewSyncLastRunAt(data.review_sync.last_run_at || null);
          setReviewSyncLastErrorAt(data.review_sync.last_error_at || null);
          setReviewSyncLastError(data.review_sync.last_error || null);
          setReviewSyncConsecutiveFailures(
            data.review_sync.consecutive_failures ?? 0
          );
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

  function handleScheduleChange(day, field, value) {
    setSyncSaved(false);
    setSyncError(null);

    setReviewSyncSchedule((current) => ({
      ...current,
      [day]: {
        ...current[day],
        [field]: value,
      },
    }));
  }

  async function handleSaveSync() {
    const interval = Number(reviewSyncInterval);

    if (
      reviewSyncInterval === "" ||
      !Number.isInteger(interval) ||
      interval <= 0
    ) {
      setSyncError(
        "El intervalo debe ser un número entero mayor que 0."
      );
      return;
    }

    try {
      setSavingSync(true);
      setSyncError(null);
      setSyncSaved(false);

      const data = await updateReviewSyncSettings(
        business.id,
        {
          enabled: reviewSyncEnabled,
          intervalMinutes: interval,
          timezone: reviewSyncTimezone,
          schedule: reviewSyncSchedule,
        }
      );

      if (data.review_sync) {
        setReviewSyncEnabled(Boolean(data.review_sync.enabled));
        setReviewSyncInterval(
          String(data.review_sync.interval_minutes)
        );
        setReviewSyncTimezone(data.review_sync.timezone);
        setReviewSyncSchedule({
          ...DEFAULT_SCHEDULE,
          ...(data.review_sync.schedule || {}),
        });

        setReviewSyncLastRunAt(data.review_sync.last_run_at || null);
        setReviewSyncLastErrorAt(data.review_sync.last_error_at || null);
        setReviewSyncLastError(data.review_sync.last_error || null);
        setReviewSyncConsecutiveFailures(
          data.review_sync.consecutive_failures ?? 0
        );
      }

      setSyncSaved(true);
    } catch (requestError) {
      setSyncError(requestError);
    } finally {
      setSavingSync(false);
    }
  }

  if (loading) {
    return (
      <div className="settings settings-state">
        <LoadingState message="Cargando configuración..." />
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
            Ajusta cómo funciona <span>{business.name}.</span>
          </h1>

          <p className="settings-intro">
            Define las reglas que Dukkah utilizará para medir el
            rendimiento y mantener actualizada la información de reseñas.
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

      <section className="settings-panel settings-sync-panel">
        <div className="settings-panel-heading">
          <div>
            <p className="panel-kicker">Google</p>
            <h2>Sincronización de reseñas</h2>
          </div>

          <span>Actualización automática</span>
        </div>

        <p className="settings-description">
          Define cuándo Dukkah puede consultar Google para detectar
          nuevas reseñas. La sincronización respeta este horario y
          utiliza el intervalo configurado.
        </p>

        <div className="settings-sync-status">
          <div>
            <strong>Sincronización automática</strong>
            <span>
              Permite que Dukkah consulte nuevas reseñas automáticamente.
            </span>
          </div>

          <label className="settings-toggle">
            <input
              type="checkbox"
              checked={reviewSyncEnabled}
              onChange={(event) => {
                setSyncSaved(false);
                setSyncError(null);
                setReviewSyncEnabled(event.target.checked);
              }}
              disabled={savingSync}
            />
            <span />
          </label>
        </div>

        <div className="settings-sync-grid">
          <div className="settings-field">
            <label htmlFor="review-sync-interval">
              Intervalo
            </label>

            <div className="settings-field-inline">
              <input
                id="review-sync-interval"
                type="number"
                min="1"
                step="1"
                value={reviewSyncInterval}
                onChange={(event) => {
                  setSyncSaved(false);
                  setSyncError(null);
                  setReviewSyncInterval(event.target.value);
                }}
                disabled={savingSync}
              />
              <span>minutos</span>
            </div>
          </div>

          <div className="settings-field">
            <label htmlFor="review-sync-timezone">
              Zona horaria
            </label>

            <input
              id="review-sync-timezone"
              type="text"
              value={reviewSyncTimezone}
              onChange={(event) => {
                setSyncSaved(false);
                setSyncError(null);
                setReviewSyncTimezone(event.target.value);
              }}
              disabled={savingSync}
            />
          </div>
        </div>

        <div className="settings-schedule">
          <div className="settings-schedule-heading">
            <div>
              <strong>Horario de sincronización</strong>
              <span>
                Solo se consultarán reseñas dentro de estos horarios.
              </span>
            </div>
          </div>

          <div className="settings-schedule-list">
            {DAYS.map(([day, label]) => (
              <div className="settings-schedule-row" key={day}>
                <strong>{label}</strong>

                <div className="settings-time-range">
                  <input
                    type="time"
                    value={reviewSyncSchedule[day]?.start || ""}
                    onChange={(event) =>
                      handleScheduleChange(
                        day,
                        "start",
                        event.target.value
                      )
                    }
                    disabled={savingSync}
                    aria-label={`${label} inicio`}
                  />

                  <span>—</span>

                  <input
                    type="time"
                    value={reviewSyncSchedule[day]?.end || ""}
                    onChange={(event) =>
                      handleScheduleChange(
                        day,
                        "end",
                        event.target.value
                      )
                    }
                    disabled={savingSync}
                    aria-label={`${label} fin`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="settings-sync-health">
          <div className="settings-sync-health-heading">
            <div>
              <strong>Estado de sincronización</strong>
              <span>
                Información de la última ejecución automática de Dukkah.
              </span>
            </div>
          </div>

          <div className="settings-sync-health-grid">
            <div className="settings-sync-health-item">
              <span>Última sincronización</span>
              <strong>
                {reviewSyncLastRunAt
                  ? new Date(reviewSyncLastRunAt).toLocaleString(
                      "es-MX",
                      {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }
                    )
                  : "Aún no se ha ejecutado"}
              </strong>
            </div>

            <div className="settings-sync-health-item">
              <span>Fallos consecutivos</span>
              <strong>
                {reviewSyncConsecutiveFailures}
              </strong>
            </div>
          </div>

          {reviewSyncLastError && (
            <div className="settings-sync-health-error">
              <strong>Último error</strong>
              <span>{reviewSyncLastError}</span>

              {reviewSyncLastErrorAt && (
                <small>
                  {new Date(reviewSyncLastErrorAt).toLocaleString(
                    "es-MX",
                    {
                      dateStyle: "medium",
                      timeStyle: "short",
                    }
                  )}
                </small>
              )}
            </div>
          )}
        </div>

        <div className="settings-actions">
          {syncError && (
            <p className="settings-action-error">
              {typeof syncError === "string"
                ? syncError
                : "No se pudo guardar la configuración de sincronización."}
            </p>
          )}

          {syncSaved && (
            <p className="settings-saved">
              Configuración de sincronización guardada.
            </p>
          )}

          <button
            type="button"
            className="settings-save-button"
            onClick={handleSaveSync}
            disabled={savingSync}
          >
            {savingSync
              ? "Guardando..."
              : "Guardar sincronización"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default Settings;
