import { useEffect, useState } from "react";
import { motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import MetricCard from "../../components/MetricCard/MetricCard";
import ErrorState from "../../components/ErrorState/ErrorState";
import {
  getAnalytics,
  getCards,
  getWaiters,
} from "../../services/api";
import "./Dashboard.css";

function Dashboard({ business }) {
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
        <p>Cargando información...</p>
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
      label: "Reseñas registradas",
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
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <p className="eyebrow">Resumen</p>

          <h1>
            Buenos días, <em>{business.name}.</em>
          </h1>
        </div>

        <p className="dashboard-date">Hoy · {today}</p>
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
            },
          },
        }}
      >
        {metrics.map((metric) => (
          <motion.div
            key={metric.label}
            variants={{
              hidden: { opacity: 0, y: 16 },
              visible: { opacity: 1, y: 0 },
            }}
            transition={{ duration: 0.45 }}
          >
            <MetricCard {...metric} />
          </motion.div>
        ))}
      </motion.section>

      <section className="dashboard-grid">
        <article className="activity-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Actividad</p>
              <h2>Interacciones a lo largo del tiempo</h2>
            </div>

            <span>Últimos 30 días</span>
          </div>

          <ActivityChart dailyTaps={analytics.daily_taps} />
        </article>

        <article className="source-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Reseñas</p>
              <h2>Estado de las atribuciones</h2>
            </div>
          </div>

          <div className="review-summary">
            <strong>{reviewAnalytics.total_review_evidence}</strong>

            <p className="review-summary-note">
              {reviewAnalytics.total_review_evidence === 0
                ? "Aún no hay reseñas registradas"
                : "Reseñas registradas en Dukkah"}
            </p>

            <div className="review-summary-row">
              <span>Atribuidas</span>
              <strong>{reviewAnalytics.attributed_reviews}</strong>
            </div>

            <div className="review-summary-row">
              <span>Sin atribución</span>
              <strong>{reviewAnalytics.unattributed_reviews}</strong>
            </div>

            <div className="review-summary-external">
              <span>Último conteo registrado</span>
              <strong>{analytics.latest_review_count}</strong>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-grid dashboard-grid-secondary">
        <article className="source-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Fuentes</p>
              <h2>Origen de las interacciones</h2>
            </div>
          </div>

          <div className="source-list">
            {sourcePercentages.map(({ label, percentage }) => (
              <div className="source-item" key={label}>
                <div className="source-meta">
                  <span>{label}</span>
                  <strong>{percentage}%</strong>
                </div>

                <div className="source-bar">
                  <motion.div
                    className="source-bar-fill"
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

        <article className="activity-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Infraestructura</p>
              <h2>Estado de Dukkah</h2>
            </div>
          </div>

          <div className="status-summary">
            <div>
              <span>Tarjetas activas</span>
              <strong>
                {activeCards} <small>/ {cards.length}</small>
              </strong>
            </div>

            <div>
              <span>Meseros activos</span>
              <strong>
                {activeWaiters} <small>/ {waiters.length}</small>
              </strong>
            </div>
          </div>
        </article>
      </section>

      <section className="waiter-panel">
        <div className="panel-heading">
          <div>
            <p className="panel-kicker">Actividad por mesero</p>
            <h2>Interacciones registradas</h2>
          </div>
        </div>

        <div className="waiter-activity">
          {waiterActivity.length === 0 ? (
            <p className="empty-state">
              Todavía no hay interacciones registradas.
            </p>
          ) : (
            waiterActivity.map((waiter, index) => (
              <div className="waiter-item" key={waiter.waiter_id}>
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
                        delay: index * 0.08,
                        ease: "easeOut",
                      }}
                    />
                  </div>
                </div>

                <strong className="waiter-total">
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

export default Dashboard;
