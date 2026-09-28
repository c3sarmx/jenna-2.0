import { motion } from "motion/react";
import "./LoadingState.css";

function LoadingState({ message = "Cargando..." }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <motion.span
        className="loading-state-line"
        initial={{ scaleX: 0.35, opacity: 0.45 }}
        animate={{ scaleX: [0.35, 1, 0.35], opacity: [0.45, 1, 0.45] }}
        transition={{
          duration: 1.6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <p>{message}</p>
    </div>
  );
}

export default LoadingState;
