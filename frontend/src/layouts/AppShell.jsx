import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  BarChart3,
  ChevronDown,
  CreditCard,
  LayoutDashboard,
  MessageSquareText,
  Settings as SettingsIcon,
  Users,
} from "lucide-react";
import Dashboard from "../pages/Dashboard/Dashboard";
import Analytics from "../pages/Analytics/Analytics";
import Cards from "../pages/Cards/Cards";
import Waiters from "../pages/Waiters/Waiters";
import Login from "../pages/Login/Login";
import Settings from "../pages/Settings/Settings";
import Reviews from "../pages/Reviews/Reviews";
import { getBusinesses, getMe, logout } from "../services/api";
import "./AppShell.css";

const navigation = [
  { id: "dashboard", label: "Resumen", icon: LayoutDashboard },
  { id: "analytics", label: "Analítica", icon: BarChart3 },
  { id: "cards", label: "Tarjetas", icon: CreditCard },
  { id: "waiters", label: "Meseros", icon: Users },
  { id: "reviews", label: "Reseñas", icon: MessageSquareText },
  {
    id: "settings",
    label: "Configuración",
    icon: SettingsIcon,
  },
];

function AppShell() {
  const [user, setUser] = useState(null);
  const [business, setBusiness] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [businessSwitcherOpen, setBusinessSwitcherOpen] = useState(false);
  const [activeView, setActiveView] = useState(() => {
    const savedView = localStorage.getItem("dukkah_active_view");

    return navigation.some((item) => item.id === savedView)
      ? savedView
      : "dashboard";
  });
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      try {
        const currentUser = await getMe();
        const businessesData = await getBusinesses();
        setUser(currentUser);
        setBusinesses(businessesData);

        const savedBusinessId = localStorage.getItem(
          "dukkah_active_business_id"
        );

        const savedBusiness = businessesData.find(
          (item) => item.id === Number(savedBusinessId)
        );

        setBusiness(savedBusiness ?? businessesData[0] ?? null);
      } catch {
        setUser(null);
        setBusiness(null);
      } finally {
        setCheckingSession(false);
      }
    }

    restoreSession();
  }, []);

  async function handleLogin(currentUser) {
    const businessesData = await getBusinesses();

    setBusinesses(businessesData);

    const savedBusinessId = localStorage.getItem(
      "dukkah_active_business_id"
    );

    const savedBusiness = businessesData.find(
      (item) => item.id === Number(savedBusinessId)
    );

    setBusiness(savedBusiness ?? businessesData[0] ?? null);
    setUser(currentUser);
  }

  async function handleLogout() {
    try {
      await logout();
    } catch {
      // Aunque el servidor falle, limpiamos la sesión local.
    } finally {
      localStorage.removeItem("dukkah_active_business_id");
      setUser(null);
      setBusiness(null);
      setBusinesses([]);
      setActiveView("dashboard");
      localStorage.removeItem("dukkah_active_view");
    }
  }

  function handleViewChange(viewId) {
    setActiveView(viewId);
    localStorage.setItem("dukkah_active_view", viewId);
  }

  function handleBusinessChange(businessId) {
    const selectedBusiness = businesses.find(
      (item) => item.id === Number(businessId)
    );

    if (!selectedBusiness) {
      return;
    }

    setBusiness(selectedBusiness);
    localStorage.setItem(
      "dukkah_active_business_id",
      String(selectedBusiness.id)

    );
    setBusinessSwitcherOpen(false);
  } 

  function renderActiveView() {
    switch (activeView) {
      case "analytics":
        return <Analytics business={business} />;

      case "cards":
        return <Cards business={business} />;

      case "waiters":
        return <Waiters business={business} />;

      case "settings":
        return <Settings business={business} />;

      case "reviews":
        return <Reviews business={business} />;

      case "dashboard":
      default:
        return <Dashboard business={business} onNavigate={handleViewChange} />;
    }
  }

  if (checkingSession) {
    return null;
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  if (!business) {
    return (
      <main className="app-empty-state">
        <p>No tienes negocios disponibles.</p>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="brand">
          <span className="brand-mark">D</span>
          <span className="brand-name">{business.name}</span>
        </div>

        <nav className="sidebar-nav" aria-label="Navegación principal">
          {navigation.map(({ id, label, icon: Icon }) => (
            <button
              className={`nav-item ${
                activeView === id ? "nav-item-active" : ""
              }`}
              key={id}
              type="button"
              onClick={() => handleViewChange(id)}
            >
              <Icon size={17} strokeWidth={1.8} />
              <span>{label}</span>

              {activeView === id && (
                <motion.span
                  className="nav-active-indicator"
                  layoutId="sidebar-active-indicator"
                  transition={{
                    type: "spring",
                    stiffness: 500,
                    damping: 35,
                    mass: 0.7,
                  }}
                />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Sistema operativo</span>
        </div>
      </aside>

      <main className="app-main">
        <header className="topbar">
          {businesses.length > 1 ? (
            <div className="business-switcher">
              <button
                className="business-switcher-trigger"
                type="button"
                onClick={() =>
                  setBusinessSwitcherOpen((open) => !open)
                }
                aria-expanded={businessSwitcherOpen}
                aria-haspopup="listbox"
              >
                <span>{business?.name}</span>
                <ChevronDown
                  size={16}
                  strokeWidth={1.8}
                  className={
                    businessSwitcherOpen
                      ? "business-switcher-chevron-open"
                      : ""
                  }
                />
              </button>

              {businessSwitcherOpen && (
                <div
                  className="business-switcher-menu"
                  role="listbox"
                >
                  <span className="business-switcher-label">
                    Negocios
                  </span>

                  {businesses.map((item) => (
                    <button
                      key={item.id}
                      className={`business-switcher-option ${
                        business?.id === item.id
                          ? "business-switcher-option-active"
                          : ""
                      }`}
                      type="button"
                      role="option"
                      aria-selected={business?.id === item.id}
                      onClick={() =>
                        handleBusinessChange(item.id)
                      }
                    >
                      <span>{item.name}</span>

                      {business?.id === item.id && (
                        <span className="business-switcher-check">
                          ✓
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <span className="business-label">
              {business?.name}
            </span>
          )}
          <div className="user-menu">
            <span className="user-label">{user.email}</span>
            <button
              className="logout-button"
              type="button"
              onClick={handleLogout}
            >
              Cerrar sesión
            </button>
          </div>
        </header>  
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{
              duration: 0.28,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            {renderActiveView()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default AppShell;
