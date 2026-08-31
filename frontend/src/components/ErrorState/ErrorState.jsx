import { RefreshCw } from "lucide-react";
import "./ErrorState.css";

function getErrorContent(error) {
  switch (error?.status) {
    case 401:
      return {
        title: "Tu sesión ya no está disponible.",
        message: "Vuelve a iniciar sesión para continuar.",
      };

    case 403:
      return {
        title: "No tienes acceso a este negocio.",
        message: "Tu cuenta no tiene permisos para consultar esta información.",
      };

    case 404:
      return {
        title: "No encontramos lo que buscas.",
        message: "El recurso solicitado ya no está disponible.",
      };

    case 500:
      return {
        title: "Ocurrió un problema en el servidor.",
        message: "Intenta nuevamente en unos momentos.",
      };

    default:
      return {
        title: "No fue posible completar la solicitud.",
        message: "Comprueba tu conexión e inténtalo nuevamente.",
      };
  }
}

function ErrorState({ error, onRetry }) {
  const { title, message } = getErrorContent(error);

  return (
    <div className="error-state">
      <div className="error-state-mark" aria-hidden="true">
        !
      </div>

      <p className="error-state-kicker">Algo salió mal</p>

      <h2>{title}</h2>

      <p>{message}</p>

      {onRetry && (
        <button
          className="error-state-button"
          type="button"
          onClick={onRetry}
        >
          <RefreshCw size={15} strokeWidth={1.8} />
          Reintentar
        </button>
      )}
    </div>
  );
}

export default ErrorState;
