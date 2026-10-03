import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "motion/react";
import "./MetricCard.css";

function AnimatedNumber({ value }) {
  const target = Number(value) || 0;
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    stiffness: 90,
    damping: 20,
    mass: 0.7,
  });

  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    motionValue.set(target);
  }, [motionValue, target]);

  useEffect(() => {
    return springValue.on("change", (latest) => {
      setDisplayValue(Math.round(latest));
    });
  }, [springValue]);

  return <>{displayValue}</>;
}

function MetricCard({ label, value, detail, growth = null, accent = false }) {
  return (
    <motion.article
      className={`metric-card ${accent ? "metric-card-accent" : ""}`}
      whileHover={{
        y: -3,
        scale: 1.008,
      }}
      whileTap={{
        scale: 0.995,
      }}
      transition={{
        type: "spring",
        stiffness: 420,
        damping: 30,
        mass: 0.8,
      }}
    >
      <div className="metric-card-header">
        <span className="metric-card-label">{label}</span>

        <span className="metric-card-indicator" aria-hidden="true">
          <span />
        </span>
      </div>

      <div className="metric-value-row">
        <motion.strong
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.45,
            ease: [0.22, 1, 0.36, 1],
          }}
        >
          <AnimatedNumber value={value} />
        </motion.strong>
      </div>

      {growth !== null && (
        <span
          className={`metric-card-growth ${
            growth >= 0
              ? "metric-card-growth-positive"
              : "metric-card-growth-negative"
          }`}
        >
          {growth >= 0 ? "↑" : "↓"} {Math.abs(growth)}% vs periodo anterior
        </span>
      )}

      <p>{detail}</p>
    </motion.article>
  );
}

export default MetricCard;
