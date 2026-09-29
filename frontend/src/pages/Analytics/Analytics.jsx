import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import ActivityChart from "../../components/ActivityChart/ActivityChart";
import ErrorState from "../../components/ErrorState/ErrorState";
import LoadingState from "../../components/LoadingState/LoadingState";
import {
  getAnalytics,
  getBusinessWeeklyAnalytics,
  getReviewAttributionEvidence,
} from "../../services/api";
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

function getCurrentWeekStart() {
  const today = new Date();
  const day = today.getDay();
  const daysSinceMonday = day === 0 ? 6 : day - 1;

  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - daysSinceMonday);

  return formatDateInput(weekStart);
}

function formatWeekRange(weekStart, weekEnd) {
  const start = new Date(`${weekStart}T00:00:00`);
  const end = new Date(`${weekEnd}T00:00:00`);

  const formatter = new Intl.DateTimeFormat("es-MX", {
    day: "numeric",
    month: "short",
  });

  return `${formatter.format(start)} — ${formatter.format(end)}`;
}

function addDaysToDate(dateString, days) {
  const date = new Date(`${dateString}T00:00:00`);
  date.setDate(date.getDate() + days);

  return formatDateInput(date);
}

function getCalendarDays(monthDate) {
  const year = monthDate.getFullYear();
  const month = monthDate.getMonth();

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const start = new Date(firstDay);
  const startDay = start.getDay();
  const daysSinceMonday = startDay === 0 ? 6 : startDay - 1;
  start.setDate(start.getDate() - daysSinceMonday);

  const end = new Date(lastDay);
  const endDay = end.getDay();
  const daysUntilSunday = endDay === 0 ? 0 : 7 - endDay;
  end.setDate(end.getDate() + daysUntilSunday);

  const days = [];
  const cursor = new Date(start);

  while (cursor <= end) {
    days.push(new Date(cursor));
    cursor.setDate(cursor.getDate() + 1);
  }

  return days;
}

function isDateInRange(dateString, start, end) {
  return (
    Boolean(start) &&
    Boolean(end) &&
    dateString >= start &&
    dateString <= end
  );
}

function Analytics({ business }) {
  const [analytics, setAnalytics] = useState(null);
  const [weeklyAnalytics, setWeeklyAnalytics] = useState(null);
  const [selectedWeekStart, setSelectedWeekStart] =
    useState(getCurrentWeekStart());
  const [isWeekPickerOpen, setIsWeekPickerOpen] = useState(false);
  const [calendarMonth, setCalendarMonth] = useState(
    new Date(`${getCurrentWeekStart()}T00:00:00`)
  );

  const [period, setPeriod] = useState("30d");
  const [loading, setLoading] = useState(true);
  const [weeklyLoading, setWeeklyLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [selectedEvidencePeriod, setSelectedEvidencePeriod] = useState(null);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [evidenceError, setEvidenceError] = useState(null);

  const selectedPeriod =
    PERIODS.find((item) => item.value === period) ?? PERIODS[2];




  function selectCalendarWeek(dateString) {
    const selectedDate = new Date(`${dateString}T00:00:00`);
    const day = selectedDate.getDay();
    const daysSinceMonday = day === 0 ? 6 : day - 1;

    const weekStartDate = new Date(selectedDate);
    weekStartDate.setDate(
      selectedDate.getDate() - daysSinceMonday
    );

    setSelectedWeekStart(formatDateInput(weekStartDate));
    setIsWeekPickerOpen(false);
  }

  function goToCurrentWeek() {
    const currentWeekStart = getCurrentWeekStart();

    setSelectedWeekStart(currentWeekStart);
    setCalendarMonth(
      new Date(`${currentWeekStart}T00:00:00`)
    );
    setIsWeekPickerOpen(false);
  }

  useEffect(() => {
    function handleWeekPickerKeyDown(event) {
      if (event.key === "Escape") {
        setIsWeekPickerOpen(false);
      }
    }

    if (isWeekPickerOpen) {
      document.addEventListener(
        "keydown",
        handleWeekPickerKeyDown
      );
    }

    return () => {
      document.removeEventListener(
        "keydown",
        handleWeekPickerKeyDown
      );
    };
  }, [isWeekPickerOpen]);

  const WEEK_DAYS = [
    ["monday", 0],
    ["tuesday", 1],
    ["wednesday", 2],
    ["thursday", 3],
    ["friday", 4],
    ["saturday", 5],
    ["sunday", 6],
  ];

  useEffect(() => {
    if (selectedEvidence === null) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [selectedEvidence]);

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

  useEffect(() => {
    function handleWeekPickerOutsideClick(event) {
      if (!isWeekPickerOpen) {
        return;
      }

      if (!event.target.closest(".weekly-picker")) {
        setIsWeekPickerOpen(false);
      }
    }

    document.addEventListener(
      "mousedown",
      handleWeekPickerOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleWeekPickerOutsideClick
      );
    };
  }, [isWeekPickerOpen]);

  useEffect(() => {
    async function loadWeeklyAnalytics() {
      try {
        setWeeklyLoading(true);

        const weeklyData = await getBusinessWeeklyAnalytics(
          business.id,
          selectedWeekStart
        );

        setWeeklyAnalytics(weeklyData);
      } catch (requestError) {
        setError(requestError);
      } finally {
        setWeeklyLoading(false);
      }
    }

    loadWeeklyAnalytics();
  }, [business.id, selectedWeekStart]);

  function handlePeriodChange(event) {
    setPeriod(event.target.value);
  }

  async function handleEvidenceClick(
    waiterId,
    dateFrom,
    dateTo,
    periodType = "day"
  ) {
    try {
      setEvidenceLoading(true);
      setSelectedEvidence([]);
      setSelectedEvidencePeriod({
        type: periodType,
        dateFrom,
        dateTo,
      });
      setEvidenceError(null);

      const evidence = await getReviewAttributionEvidence(
        business.id,
        {
          waiterId,
          dateFrom,
          dateTo,
        }
      );

      setSelectedEvidence(evidence);
    } catch (requestError) {
      setEvidenceError(requestError);
    } finally {
      setEvidenceLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="analytics analytics-state">
        <LoadingState message="Cargando analítica..." />
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

  const selectedEvidenceCount = selectedEvidence?.length ?? 0;

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
            Lo que está pasando en <span>{business.name}.</span>
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

      <section className="analytics-panel analytics-weekly">
        <div className="analytics-panel-heading">
          <div>
            <p className="panel-kicker">Rendimiento semanal</p>
            <h2>Reseñas por mesero</h2>
          </div>

          {weeklyAnalytics && (
            <div className="weekly-navigation">
              <button
                type="button"
                className="weekly-navigation-button"
                aria-label="Semana anterior"
                onClick={() =>
                  setSelectedWeekStart(
                    addDaysToDate(selectedWeekStart, -7)
                  )
                }
              >
                ‹
              </button>

              <div className="weekly-picker">
                <button
                  type="button"
                  className="weekly-navigation-range"
                  aria-expanded={isWeekPickerOpen}
                  aria-label="Seleccionar semana"
                  onClick={() => {
                    setCalendarMonth(
                      new Date(`${selectedWeekStart}T00:00:00`)
                    );
                    setIsWeekPickerOpen((open) => !open);
                  }}
                >
                  {formatWeekRange(
                    selectedWeekStart,
                    addDaysToDate(selectedWeekStart, 6)
                  )}
                  <span aria-hidden="true">⌄</span>
                </button>

                <AnimatePresence>
                  {isWeekPickerOpen && (
                    <motion.div
  className="weekly-picker-popover"
  initial={{ opacity: 0, y: -6, scale: 0.98 }}
  animate={{ opacity: 1, y: 0, scale: 1 }}
  exit={{ opacity: 0, y: -4, scale: 0.985 }}
  transition={{ duration: 0.18, ease: "easeOut" }}
>
                    <div className="weekly-picker-header">
                      <button
                        type="button"
                        className="weekly-picker-month-button"
                        aria-label="Mes anterior"
                        onClick={() => {
                          const previousMonth = new Date(
                            calendarMonth
                          );
                          previousMonth.setMonth(
                            previousMonth.getMonth() - 1
                          );
                          setCalendarMonth(previousMonth);
                        }}
                      >
                        ‹
                      </button>

                      <strong>
                        {new Intl.DateTimeFormat("es-MX", {
                          month: "long",
                          year: "numeric",
                        })
                          .format(calendarMonth)
                          .replace(" de ", " ")}
                      </strong>

                      <button
                        type="button"
                        className="weekly-picker-month-button"
                        aria-label="Mes siguiente"
                        disabled={
                          calendarMonth.getFullYear() >
                            new Date().getFullYear() ||
                          (
                            calendarMonth.getFullYear() ===
                              new Date().getFullYear() &&
                            calendarMonth.getMonth() >=
                              new Date().getMonth()
                          )
                        }
                        onClick={() => {
                          const nextMonth = new Date(calendarMonth);
                          nextMonth.setMonth(
                            nextMonth.getMonth() + 1
                          );
                          setCalendarMonth(nextMonth);
                        }}
                      >
                        ›
                      </button>
                    </div>

                    {selectedWeekStart !== getCurrentWeekStart() && (
                      <button
                        type="button"
                        className="weekly-picker-current-week"
                        onClick={goToCurrentWeek}
                      >
                        <span>Hoy</span>
                        <span>
                          {formatWeekRange(
                            getCurrentWeekStart(),
                            addDaysToDate(getCurrentWeekStart(), 6)
                          )}
                        </span>
                      </button>
                    )}

                    <div className="weekly-picker-weekdays">
                      {["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"].map(
                        (day) => (
                          <span key={day}>{day}</span>
                        )
                      )}
                    </div>

                    <div className="weekly-picker-grid">
                      {getCalendarDays(calendarMonth).map((date) => {
                        const dateString = formatDateInput(date);
                        const today = new Date();
                        const isCurrentMonth =
                          date.getMonth() === calendarMonth.getMonth();
                        const isFuture =
                          dateString > formatDateInput(today);
                        const isToday =
                          dateString === formatDateInput(today);
                        const selectedWeekEnd =
                          addDaysToDate(selectedWeekStart, 6);
                        const isStart =
                          dateString === selectedWeekStart;
                        const isEnd =
                          dateString === selectedWeekEnd;
                        const isInRange = isDateInRange(
                          dateString,
                          selectedWeekStart,
                          selectedWeekEnd
                        );

                        return (
                          <button
                            key={dateString}
                            type="button"
                            className={[
                              "weekly-picker-day",
                              isCurrentMonth
                                ? ""
                                : "weekly-picker-day-muted",
                              isInRange
                                ? "weekly-picker-day-in-range"
                                : "",
                              isStart
                                ? "weekly-picker-day-start"
                                : "",
                              isEnd
                                ? "weekly-picker-day-end"
                                : "",
                              isToday
                                ? "weekly-picker-day-today"
                                : "",
                            ]
                              .filter(Boolean)
                              .join(" ")}
                            disabled={isFuture}
                            onClick={() =>
                              selectCalendarWeek(dateString)
                            }
                          >
                            {date.getDate()}
                          </button>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
                </AnimatePresence>
              </div>

              <button
                type="button"
                className="weekly-navigation-button"
                aria-label="Semana siguiente"
                disabled={selectedWeekStart >= getCurrentWeekStart()}
                onClick={() =>
                  setSelectedWeekStart(
                    addDaysToDate(selectedWeekStart, 7)
                  )
                }
              >
                ›
              </button>
            </div>
          )}
        </div>

        <div className="weekly-review-goal">
          <div>
            <span>Meta semanal por mesero</span>
            <strong>
              {weeklyAnalytics?.weekly_reviews_per_waiter ?? "—"}
            </strong>
          </div>

          <small>reseñas atribuidas / semana</small>
        </div>

        {weeklyLoading ? (
          <LoadingState message="Cargando semana..." />
        ) : !weeklyAnalytics ||
        weeklyAnalytics.waiters.length === 0 ? (
          <p className="analytics-empty">
            Todavía no hay meseros activos para mostrar.
          </p>
        ) : (
          <div className="weekly-review-table-wrapper">
            <table className="weekly-review-table">
              <thead>
                <tr>
                  <th>Mesero</th>
                  <th>Lun</th>
                  <th>Mar</th>
                  <th>Mié</th>
                  <th>Jue</th>
                  <th>Vie</th>
                  <th>Sáb</th>
                  <th>Dom</th>
                  <th>Total</th>
                  <th>Alcance</th>
                </tr>
              </thead>

              <tbody>
                {weeklyAnalytics.waiters.map((waiter) => (
                  <tr key={waiter.waiter_id}>
                    <th scope="row">{waiter.waiter_name}</th>

                    {WEEK_DAYS.map(([day, offset]) => {
                      const count = waiter.daily[day];

                      if (count === 0) {
                        return <td key={day}>0</td>;
                      }

                      const date = addDaysToDate(
                        weeklyAnalytics.week_start,
                        offset
                      );

                      return (
                        <td key={day}>
                          <button
                            type="button"
                            className="weekly-review-link"
                            onClick={() =>
                              handleEvidenceClick(
                                waiter.waiter_id,
                                date,
                                date,
                                "day"
                              )
                            }
                          >
                            {count}
                          </button>
                        </td>
                      );
                    })}

                    <td className="weekly-review-total">
                      {waiter.total === 0 ? (
                        0
                      ) : (
                        <button
                          type="button"
                          className="weekly-review-link"
                          onClick={() =>
                            handleEvidenceClick(
                              waiter.waiter_id,
                              weeklyAnalytics.week_start,
                              weeklyAnalytics.week_end,
                              "week"
                            )
                          }
                        >
                          {waiter.total}
                        </button>
                      )}
                    </td>

                    <td className="weekly-review-reach">
                      {waiter.reach_percentage !== null
                        ? `${waiter.reach_percentage}%`
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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
      {selectedEvidence !== null && (
        <div
          className="review-evidence-overlay"
          role="presentation"
          onClick={() => setSelectedEvidence(null)}
        >
          <section
            className="review-evidence-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Evidencia de reviews"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="review-evidence-header">
              <div>
                <p className="review-evidence-eyebrow">EVIDENCIA</p>
                <h2>
                  {selectedEvidence?.[0]?.waiter_name || "Mesero"}
                </h2>
                <p>
                  {evidenceLoading ? (
                    "Cargando evidencia..."
                  ) : (
                    <>
                      {selectedEvidenceCount}{" "}
                      {selectedEvidenceCount === 1
                        ? "review atribuida"
                        : "reviews atribuidas"}

                      {selectedEvidencePeriod?.type === "week" ? (
                        <>
                          {" · semana del "}
                          {new Date(
                            `${selectedEvidencePeriod.dateFrom}T00:00:00`
                          ).toLocaleDateString("es-MX", {
                            day: "numeric",
                            month: "short",
                          })}
                          {" al "}
                          {new Date(
                            `${selectedEvidencePeriod.dateTo}T00:00:00`
                          ).toLocaleDateString("es-MX", {
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          })}
                        </>
                      ) : selectedEvidence?.[0]?.published_at ? (
                        <>
                          {" · "}
                          {new Date(
                            selectedEvidence[0].published_at
                          ).toLocaleDateString("es-MX", {
                            weekday: "long",
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          })}
                        </>
                      ) : null}
                    </>
                  )}
                </p>
              </div>

              <button
                type="button"
                className="review-evidence-close"
                onClick={() => setSelectedEvidence(null)}
                aria-label="Cerrar"
              >
                ×
              </button>
            </div>

            {evidenceLoading && (
              <div className="review-evidence-state">
                Cargando evidencia...
              </div>
            )}

            {!evidenceLoading && evidenceError && (
              <div className="review-evidence-state review-evidence-error">
                No fue posible cargar la evidencia.
              </div>
            )}

            {!evidenceLoading &&
              !evidenceError &&
              selectedEvidenceCount === 0 && (
                <div className="review-evidence-state">
                  No hay evidencia disponible para este periodo.
                </div>
              )}

            {!evidenceLoading &&
              !evidenceError &&
              selectedEvidenceCount > 0 && (
                <div className="review-evidence-list">
                  {selectedEvidence.map((review) => (
                    <article
                      key={review.id}
                      className="review-evidence-card"
                    >
                      <div className="review-evidence-card-header">
                        <div>
                          <strong>
                            {review.reviewer_name || "Cliente"}
                          </strong>
                          <span>
                            {review.published_at
                              ? new Date(
                                  review.published_at
                                ).toLocaleDateString("es-MX", {
                                  day: "numeric",
                                  month: "short",
                                  year: "numeric",
                                })
                              : "Fecha no disponible"}
                          </span>
                        </div>

                        <span className="review-evidence-rating">
                          {"★".repeat(review.rating || 0)}
                        </span>
                      </div>

                      <p className="review-evidence-content">
                        {review.translated_content || review.content}
                      </p>

                      <div className="review-evidence-meta">
                        <span>
                          Confianza:{" "}
                          {review.confidence === "high"
                            ? "Alta"
                            : review.confidence === "medium"
                              ? "Media"
                              : review.confidence === "low"
                                ? "Baja"
                                : "No disponible"}
                        </span>
                        <span>
                          Criterio:{" "}
                          {review.method === "name_match"
                            ? "Nombre mencionado en la reseña"
                            : review.method === "manual"
                              ? "Confirmación manual"
                              : review.method || "No disponible"}
                        </span>
                      </div>
                    </article>
                  ))}
                </div>
              )}
          </section>
        </div>
      )}

      </div>
  );
}

export default Analytics;
