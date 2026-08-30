import { useEffect, useState } from "react";
import { motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import MetricCard from "../../components/MetricCard/MetricCard";
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
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [business.id]);

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
        <p>No fue posible cargar la información.</p>
        <span>{error}</span>
      </div>
    );
  }

  console.log("ANALYTICS:", analytics);
  console.log("DAILY TAPS:", analytics?.daily_taps);

  const activeCards = cards.filter((card) => card.active).length;
  const activeWaiters = waiters.filter((waiter) => waiter.active).length;

  const metrics = [
    {
      label: "Interacciones",
      value: analytics.total_taps,
      detail: "Durante el periodo seleccionado",
      accent: true,
    },
    {
      label: "Tarjetas",
      value: cards.length,
      detail: `${activeCards} actualmente activas`,
    },
    {
      label: "Meseros",
      value: waiters.length,
      detail: `${activeWaiters} actualmente activos`,
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
              <p className="panel-kicker">Fuentes</p>
              <h2>Cómo conectan tus clientes</h2>
            </div>
          </div>

          <div className="source-list">
            {sourcePercentages.map(
              ({ label, percentage }) => (
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
              )
            )}
          </div>
        </article>
      </section>
    </div>
  );
}

export default Dashboard;
