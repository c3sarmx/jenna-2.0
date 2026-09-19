import { motion } from "motion/react";
import "./ActivityChart.css";

function formatDate(dateString) {
  const [year, month, day] = dateString.slice(0, 10).split("-");

  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
  }).format(new Date(Number(year), Number(month) - 1, Number(day)));
}

function ActivityChart({ dailyTaps = [], periodLabel = "Últimos 30 días" }) {
  const values = dailyTaps.map((item) => item.total_taps);
  const maxValue = Math.max(...values, 1);

  const points = dailyTaps.map((item, index) => {
    const x =
      dailyTaps.length === 1
        ? 50
        : (index / (dailyTaps.length - 1)) * 100;

    const y = 140 - (item.total_taps / maxValue) * 100;

    return [x, y];
  });

  const line = points.map(([x, y]) => `${x},${y}`).join(" ");
  const area = `0,150 ${line} 100,150`;

  const axisIndexes = [
    0,
    Math.floor((dailyTaps.length - 1) * 0.25),
    Math.floor((dailyTaps.length - 1) * 0.5),
    Math.floor((dailyTaps.length - 1) * 0.75),
    dailyTaps.length - 1,
  ];

  return (
    <div className="activity-chart">
      <div className="chart-grid">
        <span />
        <span />
        <span />
        <span />
      </div>

      <svg
        className="chart-svg"
        viewBox="0 0 100 150"
        preserveAspectRatio="none"
        role="img"
        aria-label={`Evolución de interacciones durante ${periodLabel.toLowerCase()}`}
      >
        {points.length > 0 && (
          <>
            <motion.polygon
              points={area}
              className="chart-area"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.25 }}
            />

            <motion.polyline
              points={line}
              className="chart-path"
              pathLength="1"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1.2,
                ease: "easeOut",
              }}
            />

            <motion.circle
              cx={points[points.length - 1][0]}
              cy={points[points.length - 1][1]}
              r="1.7"
              className="chart-point"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                delay: 1.05,
                duration: 0.3,
              }}
            />
          </>
        )}
      </svg>

      <div className="chart-axis">
        {dailyTaps.length > 0 ? (
          axisIndexes.map((index) => (
            <span key={index}>
              {formatDate(dailyTaps[index].date)}
            </span>
          ))
        ) : (
          <span>Sin datos</span>
        )}
      </div>
    </div>
  );
}

export default ActivityChart;
