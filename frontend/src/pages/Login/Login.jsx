import { useState } from "react";
import { motion } from "motion/react";
import { login } from "../../services/api";
import "./Login.css";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const user = await login(email, password);
      await onLogin(user);
    } catch {
      setError("El correo o la contraseña no son correctos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <motion.section
        className="login-card"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="login-brand">
          <span className="login-mark">D</span>
          <span>Dukkah</span>
        </div>

        <div className="login-heading">
          <p className="eyebrow">Acceso</p>
          <h1>Bienvenido de nuevo.</h1>
          <p>
            Entra para ver lo que está pasando en tu negocio.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Correo electrónico
            <input
              type="email"
              name="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="tu@negocio.com"
              autoComplete="email"
              required
            />
          </label>

          <label>
            Contraseña
            <input
              type="password"
              name="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </label>

          {error && <p className="login-error">{error}</p>}

          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: 0.98 }}
            whileHover={{ y: -1 }}
          >
            {loading ? "Entrando..." : "Entrar"}
          </motion.button>
        </form>
      </motion.section>

      <p className="login-footer">
        Dukkah · Tu negocio, en movimiento.
      </p>
    </main>
  );
}

export default Login;
