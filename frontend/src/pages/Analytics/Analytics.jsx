import { useEffect, useState } from "react";
import { motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import ErrorState from "../../components/ErrorState/ErrorState";
import { getAnalytics } from "../../services/api";
import "./Analytics.css";

const PERIODS = [
  { value: "today", label: "Hoy", days: 1 },
  { value: "7d", label: "Últimos 7 días", days: 7 },
  { value: "30d", label: "Últimos 30 días", days: 30 },
  { value: "90d", label: "Últimos 90 días", days: 90 },
];

function formatDateInput(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getPeriodDates(days) {
  const today = new Date();
  const dateTo = formatDateInput(today);

  const dateFromValue = new Date(today);
  dateFromValue.setDate(today.getDate() - (days - 1));

  return {
    dateFrom: formatDateInput(dateFromValue),
    dateTo,
  };
}

function Analytics({ business }) {
  const [analytics, setAnalytics] = useState(null);
  const [period, setPeriod] = useState("30d");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  const selectedPeriod =
    PERIODS.find((item) => item.value === period) ?? PERIODS[2];

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        setError(null);

        const { dateFrom, dateTo } = getPeriodDates(
          selectedPeriod.days
        );

        const data = await getAnalytics(business.id, {
          dateFrom,
          dateTo,
        });

        setAnalytics(data);
      } catch (requestError) {
        setError(requestError);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, [business.id, selectedPeriod.days, retryKey]);

  function handlePeriodChange(event) {
    setPeriod(event.target.value);
  }

  if (loading) {
    return (
      <div className="analytics analytics-state">
        <p>Cargando analítica...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics analytics-state">
        <ErrorState
          error={error}
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  const reviewAnalytics = analytics.review_analytics ?? {
    total_review_evidence: 0,
    attributed_reviews: 0,
    unattributed_reviews: 0,
    reviews_by_waiter: [],
  };

  const sources = [
    {
      label: "NFC",
      value: analytics.taps_by_source.nfc,
    },
    {
      label: "QR",
      value: analytics.taps_by_source.qr,
    },
    {
      label: "Web",
      value: analytics.taps_by_source.web,
    },
  ];

  const totalSourceTaps = sources.reduce(
    (total, source) => total + source.value,
    0
  );

  const sourcePercentages = sources.map((source) => ({
    ...source,
    percentage:
      totalSourceTaps > 0
        ? Math.round((source.value / totalSourceTaps) * 100)
        : 0,
  }));

  const waiterRanking = [...analytics.taps_by_waiter].sort(
    (a, b) => b.total_taps - a.total_taps
  );

  return (
    <div className="analytics">
      <motion.header
        className="analytics-header"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <p className="eyebrow">Analítica</p>

          <h1>
            Lo que está pasando en <em>{business.name}.</em>
          </h1>

          <p className="analytics-intro">
            Entiende cómo interactúan tus clientes con Dukkah.
          </p>
        </div>

        <label className="analytics-period-control">
          <span className="sr-only">Periodo de análisis</span>

          <select
            value={period}
            onChange={handlePeriodChange}
            aria-label="Periodo de análisis"
          >
            {PERIODS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
      </motion.header>

      <motion.section
        className="analytics-summary"
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
        <motion.article
          className="analytics-card"
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          <span>Interacciones</span>
          <strong>{analytics.total_taps}</strong>
          <p>{selectedPeriod.label}</p>
        </motion.article>

        <motion.article
          className="analytics-card"
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          <span>Reseñas registradas</span>
          <strong>{reviewAnalytics.total_review_evidence}</strong>
          <p>Dentro de Dukkah</p>
        </motion.article>

        <motion.article
          className="analytics-card"
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          <span>Con atribución</span>
          <strong>{reviewAnalytics.attributed_reviews}</strong>
          <p>Reseñas con atribución</p>
        </motion.article>
      </motion.section>

      <section className="analytics-panel analytics-activity">
        <div className="analytics-panel-heading">
          <div>
            <p className="panel-kicker">Actividad</p>
            <h2>Interacciones a lo largo del tiempo</h2>
          </div>

          <span>{selectedPeriod.label}</span>
        </div>

        <ActivityChart
          dailyTaps={analytics.daily_taps}
          periodLabel={selectedPeriod.label}
        />
      </section>

      <section className="analytics-grid">
        <article className="analytics-panel analytics-sources">
          <div className="analytics-panel-heading">
            <div>
              <p className="panel-kicker">Fuentes</p>
              <h2>Origen de las interacciones</h2>
            </div>
          </div>

          <div className="analytics-source-list">
            {sourcePercentages.map(({ label, value, percentage }) => (
              <div className="analytics-source" key={label}>
                <div className="analytics-source-meta">
                  <div>
                    <span>{label}</span>
                    <small>{value} interacciones</small>
                  </div>

                  <strong>{percentage}%</strong>
                </div>

                <div className="analytics-source-bar">
                  <motion.div
                    className="analytics-source-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{
                      duration: 0.8,
                      delay: 0.2,
                      ease: "easeOut",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="analytics-panel analytics-reviews">
          <div className="analytics-panel-heading">
            <div>
              <p className="panel-kicker">Reseñas</p>
              <h2>Estado de las atribuciones</h2>
            </div>
          </div>

          <div className="analytics-review-summary">
            <div className="analytics-review-total">
              <strong>{reviewAnalytics.total_review_evidence}</strong>
              <span>Registradas en Dukkah</span>
            </div>

            <div className="analytics-review-row">
              <span>Atribuidas</span>
              <strong>{reviewAnalytics.attributed_reviews}</strong>
            </div>

            <div className="analytics-review-row">
              <span>Sin atribución</span>
              <strong>{reviewAnalytics.unattributed_reviews}</strong>
            </div>

            <div className="analytics-review-row">
              <span>Último conteo registrado</span>
              <strong>{analytics.latest_review_count}</strong>
            </div>
          </div>
        </article>
      </section>

      <section className="analytics-panel analytics-ranking">
        <div className="analytics-panel-heading">
          <div>
            <p className="panel-kicker">Actividad por mesero</p>
            <h2>Interacciones registradas</h2>
          </div>
        </div>

        <div className="waiter-ranking">
          {waiterRanking.length === 0 ? (
            <p className="analytics-empty">
              Todavía no hay interacciones registradas.
            </p>
          ) : (
            waiterRanking.map((waiter, index) => (
              <div
                className="waiter-ranking-item"
                key={waiter.waiter_id}
              >
                <span className="waiter-ranking-position">
                  {String(index + 1).padStart(2, "0")}
                </span>

                <div className="waiter-ranking-info">
                  <strong>{waiter.waiter_name}</strong>

                  <div className="waiter-ranking-bar">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{
                        width: `${
                          analytics.total_taps > 0
                            ? (waiter.total_taps /
                                analytics.total_taps) *
                              100
                            : 0
                        }%`,
                      }}
                      transition={{
                        duration: 0.8,
                        delay: index * 0.08,
                        ease: "easeOut",
                      }}
                    />
                  </div>
                </div>

                <strong className="waiter-ranking-total">
                  {waiter.total_taps}
                </strong>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}

export default Analytics;
