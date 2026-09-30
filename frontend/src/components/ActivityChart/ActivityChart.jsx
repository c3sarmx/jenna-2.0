import { useMemo, useState } from "react";
import { motion } from "motion/react";
import "./ActivityChart.css";

function formatDate(dateString) {
  const [year, month, day] = dateString.slice(0, 10).split("-");
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
  }).format(new Date(Number(year), Number(month) - 1, Number(day)));
}

function formatLongDate(dateString) {
  const [year, month, day] = dateString.slice(0, 10).split("-");
  return new Intl.DateTimeFormat("es-MX", {
    day: "numeric",
    month: "long",
  }).format(new Date(Number(year), Number(month) - 1, Number(day)));
}

function ActivityChart({
  dailyTaps = [],
  periodLabel = "Últimos 30 días",
}) {
  const [activeIndex, setActiveIndex] = useState(null);

  const maxValue = Math.max(
    ...dailyTaps.map((item) => {
      const value = Number(item?.total_taps);
      return Number.isFinite(value) ? value : 0;
    }),
    1
  );

  const normalizedData = useMemo(
    () =>
      dailyTaps.map((item) => ({
        ...item,
        total_taps: Number.isFinite(Number(item?.total_taps))
          ? Number(item.total_taps)
          : 0,
      })),
    [dailyTaps]
  );

  const hasActivity = normalizedData.some((item) => item.total_taps > 0);

  const points = useMemo(() => {
    return normalizedData.map((item, index) => {
      const x =
        normalizedData.length === 1
          ? 50
          : 2 + (index / (normalizedData.length - 1)) * 96;

      const value = item.total_taps;
      const y = 12 + (1 - value / maxValue) * 76;

      return [x, y];
    });
  }, [normalizedData, maxValue]);

  const linePoints = useMemo(
    () => points.map(([x, y]) => `${x},${y}`).join(" "),
    [points]
  );

  const areaPoints = useMemo(() => {
    if (!points.length) return "";

    return [
      ...points.map(([x, y]) => `${x},${y}`),
      `${points[points.length - 1][0]},92`,
      `${points[0][0]},92`,
    ].join(" ");
  }, [points]);

  const axisIndexes = [...new Set([
    0,
    Math.floor((dailyTaps.length - 1) * 0.25),
    Math.floor((dailyTaps.length - 1) * 0.5),
    Math.floor((dailyTaps.length - 1) * 0.75),
    dailyTaps.length - 1,
  ])];

  const activePoint =
    activeIndex !== null && points[activeIndex]
      ? {
          point: points[activeIndex],
          data: dailyTaps[activeIndex],
        }
      : null;

  return (
    <div
      className="activity-chart"
      onMouseLeave={() => setActiveIndex(null)}
    >
      {hasActivity && (
        <div className="chart-y-axis" aria-hidden="true">
          <span>{maxValue}</span>
          <span>{Math.round(maxValue * 0.66)}</span>
          <span>{Math.round(maxValue * 0.33)}</span>
          <span>0</span>
        </div>
      )}

      <svg
        className="chart-svg"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        role="img"
        aria-label={`Evolución de interacciones durante ${periodLabel.toLowerCase()}`}
      >
        <defs>
          <linearGradient
            id="activity-area-gradient"
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
            <stop
              offset="0%"
              stopColor="var(--color-accent)"
              stopOpacity="0.18"
            />
            <stop
              offset="100%"
              stopColor="var(--color-accent)"
              stopOpacity="0"
            />
          </linearGradient>
        </defs>

        {hasActivity && (
          <g className="chart-grid-lines">
            <line x1="0" y1="12" x2="100" y2="12" />
            <line x1="0" y1="38" x2="100" y2="38" />
            <line x1="0" y1="64" x2="100" y2="64" />
            <line x1="0" y1="92" x2="100" y2="92" />
          </g>
        )}

        {hasActivity && points.length > 0 && (
          <>
            <motion.polygon
              points={areaPoints}
              className="chart-area"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
            />

            <polyline
              points={linePoints}
              className="chart-path"
              fill="none"
            />

            {points.map(([x, y], index) => {
              const isActive = index === activeIndex;
              const isLast = index === points.length - 1;

              return (
                <g key={`${normalizedData[index].date}-${index}`}>
                  <circle
                    className="chart-hit-area"
                    cx={x}
                    cy={y}
                    r="5"
                    onMouseEnter={() => setActiveIndex(index)}
                    onFocus={() => setActiveIndex(index)}
                    onClick={() => setActiveIndex(index)}
                    tabIndex={0}
                    role="button"
                    aria-label={`${formatLongDate(
                      dailyTaps[index].date
                    )}: ${normalizedData[index].total_taps} interacciones`}
                  />

                  {(isActive || isLast) && (
                    <motion.circle
                      cx={x}
                      cy={y}
                      className="chart-point"
                      initial={{ scale: 0 }}
                      animate={{ scale: isActive ? 1.5 : 1 }}
                      transition={{
                        type: "spring",
                        stiffness: 400,
                        damping: 25,
                      }}
                    />
                  )}
                </g>
              );
            })}

            {activePoint && (
              <motion.line
                className="chart-focus-line"
                x1={activePoint.point[0]}
                x2={activePoint.point[0]}
                y1="8"
                y2="92"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              />
            )}
          </>
        )}
      </svg>

      {!hasActivity && normalizedData.length > 0 && (
        <div className="chart-empty-state">
          <strong>Sin interacciones todavía</strong>
          <span>
            Las interacciones de los últimos 30 días aparecerán aquí.
          </span>
        </div>
      )}

      {activePoint && (
        <motion.div
          className="chart-tooltip"
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            type: "spring",
            stiffness: 420,
            damping: 28,
          }}
          style={{
            left: `${Math.min(
              Math.max(activePoint.point[0], 10),
              90
            )}%`,
            top: `${Math.max(
              (activePoint.point[1] / 100) * 100 - 18,
              2
            )}%`,
          }}
        >
          <span>{formatLongDate(activePoint.data.date)}</span>
          <strong>
            {activePoint.data.total_taps}{" "}
            {activePoint.data.total_taps === 1
              ? "interacción"
              : "interacciones"}
          </strong>
        </motion.div>
      )}

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
