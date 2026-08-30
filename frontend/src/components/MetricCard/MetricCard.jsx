import { motion } from "motion/react";
import "./MetricCard.css";

function MetricCard({ label, value, detail, accent = false }) {
  return (
    <motion.article
      className={`metric-card ${accent ? "metric-card-accent" : ""}`}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      <div className="metric-card-header">
        <span>{label}</span>
        <span className="metric-card-dot" />
      </div>

      <div className="metric-value-row">
        <strong>{value}</strong>
      </div>

      <p>{detail}</p>
    </motion.article>
  );
}

export default MetricCard;
