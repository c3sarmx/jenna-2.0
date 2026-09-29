import { useEffect, useState } from "react";
import { motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import MetricCard from "../../components/MetricCard/MetricCard";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import {
  getAnalytics,
  getCards,
  getWaiters,
} from "../../services/api";
import "./Dashboard.css";

function getGreeting() {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) {
    return "Buenos días,";
  }

  if (hour >= 12 && hour < 19) {
    return "Buenas tardes,";
  }

  return "Buenas noches,";
}

const SHOW_SOURCE_ANALYTICS = false;

function Dashboard({ business, onNavigate }) {
  const [analytics, setAnalytics] = useState(null);
  const [cards, setCards] = useState([]);
  const [waiters, setWaiters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [analyticsData, cardsData, waitersData] =
          await Promise.all([
            getAnalytics(business.id),
            getCards(business.id),
            getWaiters(business.id),
          ]);

        setAnalytics(analyticsData);
        setCards(cardsData);
        setWaiters(waitersData);
      } catch (requestError) {
        setError(requestError);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [business.id, retryKey]);

  if (loading) {
    return (
      <div className="dashboard dashboard-state">
        <LoadingState message="Cargando información..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard dashboard-state">
        <ErrorState
          error={error}
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  const activeCards = cards.filter((card) => card.active).length;
  const activeWaiters = waiters.filter((waiter) => waiter.active).length;

  const reviewAnalytics = analytics.review_analytics ?? {
    total_review_evidence: 0,
    attributed_reviews: 0,
    unattributed_reviews: 0,
    reviews_by_waiter: [],
  };

  const statusTitle =
    cards.length === 0 || waiters.length === 0
      ? "Configuración pendiente"
      : activeCards === cards.length && activeWaiters === waiters.length
        ? "Todo en orden"
        : "Requiere atención";

  const waiterStatusDetail =
    waiters.length === 0
      ? "Sin meseros registrados"
      : activeWaiters === waiters.length
        ? "Todos los meseros están activos"
        : activeWaiters === 0
          ? "Ningún mesero activo"
          : `${activeWaiters} de ${waiters.length} activos`;

  const metrics = [
    {
      label: "Interacciones",
      value: analytics.total_taps,
      detail: "Durante el periodo seleccionado",
      accent: true,
    },
    {
      label: "Reseñas",
      value: reviewAnalytics.total_review_evidence,
      detail: `${reviewAnalytics.attributed_reviews} con atribución`,
    },
    {
      label: "Meseros activos",
      value: activeWaiters,
      detail: waiterStatusDetail,
    },
  ];

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

  const waiterActivity = [...analytics.taps_by_waiter]
    .sort((a, b) => b.total_taps - a.total_taps)
    .slice(0, 5);

  const maxWaiterTaps = waiterActivity[0]?.total_taps ?? 0;

  const today = new Date().toLocaleDateString("es-MX", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="dashboard">
      <motion.header
        className="dashboard-header"
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.65,
          ease: [0.22, 1, 0.36, 1],
        }}
      >
        <div className="dashboard-intro">
          <p className="eyebrow">Resumen</p>

          <h1>
            {getGreeting()} <span>{business.name}.</span>
          </h1>

          <p className="dashboard-description">
            Una vista tranquila de lo que está pasando con tu equipo.
          </p>
        </div>

        <time className="dashboard-date">
          Hoy · {today}
        </time>
      </motion.header>

      <motion.section
        className="metrics-grid"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: {
            transition: {
              staggerChildren: 0.08,
              delayChildren: 0.12,
            },
          },
        }}
      >
        {metrics.map((metric) => (
          <motion.div
            key={metric.label}
            className={`metric-slot ${
              metric.accent ? "metric-slot-primary" : ""
            }`}
            variants={{
              hidden: {
                opacity: 0,
                y: 18,
              },
              visible: {
                opacity: 1,
                y: 0,
              },
            }}
            transition={{
              duration: 0.55,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            <MetricCard {...metric} />
          </motion.div>
        ))}
      </motion.section>

      <section className="dashboard-primary">
        <motion.article
          className="activity-panel"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.6,
            delay: 0.3,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Actividad</p>
              <h2>Interacciones</h2>
            </div>

            <span>Últimos 30 días</span>
          </div>

          <ActivityChart dailyTaps={analytics.daily_taps} />
        </motion.article>

        <motion.article
          className="review-panel"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.6,
            delay: 0.38,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Reseñas</p>
              <h2>Lo que llega al negocio</h2>
            </div>
          </div>

          <div className="review-summary">
            <strong>{reviewAnalytics.total_review_evidence}</strong>

            <p className="review-summary-note">
              {reviewAnalytics.total_review_evidence === 0
                ? "Todavía no hay reseñas registradas."
                : "Reseñas registradas en Dukkah."}
            </p>

            {reviewAnalytics.total_review_evidence === 0 && (
              <div className="review-empty-status">
                <span aria-hidden="true" />
                <span>Las reseñas públicas se revisan automáticamente.</span>
              </div>
            )}

            {reviewAnalytics.attributed_reviews > 0 ? (
              <button
                className="review-summary-row review-summary-action"
                type="button"
                onClick={() => onNavigate?.("reviews")}
              >
                <span>Atribuidas</span>
                <span className="review-summary-action-value">
                  <strong>{reviewAnalytics.attributed_reviews}</strong>
                  <span className="review-summary-action-arrow" aria-hidden="true">
                    →
                  </span>
                </span>
              </button>
            ) : (
              <div className="review-summary-row">
                <span>Atribuidas</span>
                <strong>0</strong>
              </div>
            )}

            <div className="review-summary-row">
              <span>Sin atribución</span>
              <strong>{reviewAnalytics.unattributed_reviews}</strong>
            </div>

            <div className="review-summary-external">
              <span>Reseñas en Google</span>
              <strong>{analytics.latest_review_count}</strong>
            </div>
          </div>
        </motion.article>
      </section>

      <section className="dashboard-secondary">
        {SHOW_SOURCE_ANALYTICS && (
          <motion.article
            className="source-panel"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.55,
            delay: 0.42,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Origen</p>
              <h2>Cómo llegan las interacciones</h2>
            </div>
          </div>

          <div className="source-list">
            {sourcePercentages.map(({ label, value, percentage }) => (
              <div className="source-item" key={label}>
                <div className="source-meta">
                  <div>
                    <span>{label}</span>
                    <small>{value} interacciones</small>
                  </div>

                  <strong>{percentage}%</strong>
                </div>

                <div className="source-bar">
                  <motion.div
                    className="source-bar-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{
                      duration: 0.9,
                      delay: 0.5,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
          </motion.article>
        )}

        <motion.article
          className="status-panel"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.55,
            delay: 0.48,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Estado</p>
              <h2>{statusTitle}</h2>
            </div>
          </div>

          <div className="status-summary">
            <div>
              <span>Tarjetas activas</span>
              <strong>
                {activeCards}
                <small>/ {cards.length}</small>
              </strong>
            </div>

            <div>
              <span>Meseros activos</span>
              <strong>
                {activeWaiters}
                <small>/ {waiters.length}</small>
              </strong>
            </div>
          </div>
        </motion.article>
      </section>

      <motion.section
        className="waiter-panel"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.55,
          delay: 0.54,
          ease: [0.22, 1, 0.36, 1],
        }}
      >
        <div className="panel-heading">
          <div>
            <p className="panel-kicker">Equipo</p>
            <h2>Interacciones por mesero</h2>
          </div>

          <span>Top 5</span>
        </div>

        <div className="waiter-activity">
          {waiterActivity.length === 0 ? (
            <p className="empty-state">
              Todavía no hay interacciones registradas.
            </p>
          ) : (
            waiterActivity.map((waiter, index) => (
              <motion.div
                className="waiter-item"
                key={waiter.waiter_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  delay: 0.58 + index * 0.06,
                  duration: 0.4,
                }}
              >
                <span className="waiter-index">
                  {String(index + 1).padStart(2, "0")}
                </span>

                <div className="waiter-info">
                  <strong>{waiter.waiter_name}</strong>

                  <div className="waiter-bar">
                    <motion.div
                      className="waiter-bar-fill"
                      initial={{ width: 0 }}
                      animate={{
                        width:
                          maxWaiterTaps > 0
                            ? `${(waiter.total_taps / maxWaiterTaps) * 100}%`
                            : "0%",
                      }}
                      transition={{
                        duration: 0.8,
                        delay: 0.65 + index * 0.08,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                    />
                  </div>
                </div>

                <strong className="waiter-total">
                  {waiter.total_taps}
                </strong>
              </motion.div>
            ))
          )}
        </div>
      </motion.section>
    </div>
  );
}

export default Dashboard;
