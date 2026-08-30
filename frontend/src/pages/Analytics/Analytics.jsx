import { useEffect, useState } from "react";
import { motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import { getAnalytics } from "../../services/api";
import "./Analytics.css";

function Analytics({ business }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        setError(null);

        const data = await getAnalytics(business.id);

        setAnalytics(data);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, [business.id]);

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
        <p>No fue posible cargar la analítica.</p>
        <span>{error}</span>
      </div>
    );
  }

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

        <span className="analytics-period">
          Últimos 30 días
        </span>
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
          <p>Durante el periodo</p>
        </motion.article>

        <motion.article
          className="analytics-card"
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          <span>Reseñas</span>
          <strong>{analytics.latest_review_count ?? 0}</strong>
          <p>Último registro disponible</p>
        </motion.article>

        <motion.article
          className="analytics-card"
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          <span>Meseros</span>
          <strong>{analytics.total_waiters}</strong>
          <p>Registrados en el negocio</p>
        </motion.article>
      </motion.section>

      <section className="analytics-grid">
        <article className="analytics-panel analytics-activity">
          <div className="analytics-panel-heading">
            <div>
              <p className="panel-kicker">Actividad</p>
              <h2>Interacciones a lo largo del tiempo</h2>
            </div>

            <span>30 días</span>
          </div>

          <ActivityChart dailyTaps={analytics.daily_taps} />
        </article>

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
      </section>

      <section className="analytics-panel analytics-ranking">
        <div className="analytics-panel-heading">
          <div>
            <p className="panel-kicker">Rendimiento</p>
            <h2>Interacciones por mesero</h2>
          </div>
        </div>

        <div className="waiter-ranking">
          {analytics.taps_by_waiter.map((waiter, index) => (
            <div className="waiter-ranking-item" key={waiter.waiter_id}>
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
          ))}
        </div>
      </section>
    </div>
  );
}

export default Analytics;
