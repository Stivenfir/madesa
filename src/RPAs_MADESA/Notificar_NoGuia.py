from __future__ import annotations

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import json
import os
import smtplib
from typing import Iterable

from RPAs_MADESA.Bases import Utils

# Lista de destinatarios del equipo de soporte (editar según necesidad)
DESTINATARIOS_MESA_AYUDA = [
    "mesaayuda@abcrepecev.com",
]

# Correo en tabla dbo.Login365 que se usa para autenticación OAuth/Graph
CORREO_365 = "mesaayuda@abcrepecev.com"

# Endpoints de Office 365
GRAPH_SENDMAIL_URL = "https://graph.microsoft.com/v1.0/me/sendMail"
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587

# Archivo para evitar reenvíos duplicados del mismo pedido
PATH_ESTADO_NOTIFICACIONES = os.path.join(Utils.PATH_txt, "notificados_sin_guia.json")


def _bool_env(var_name: str, default: bool = False) -> bool:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _destinatarios_desde_env() -> list[str]:
    raw = os.getenv("NOTIFICAR_DESTINATARIOS", "").strip()
    if not raw:
        return DESTINATARIOS_MESA_AYUDA
    return [correo.strip() for correo in raw.split(",") if correo.strip()]


def _cargar_estado_notificados() -> set[str]:
    if not os.path.exists(PATH_ESTADO_NOTIFICACIONES):
        return set()
    with open(PATH_ESTADO_NOTIFICACIONES, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return set()
    return set(str(x) for x in data)


def _guardar_estado_notificados(pedidos: Iterable[str]) -> None:
    with open(PATH_ESTADO_NOTIFICACIONES, "w", encoding="utf-8") as file:
        json.dump(sorted(list(pedidos)), file, ensure_ascii=False, indent=2)


def _obtener_token_login365(correo: str) -> str:
    Utils.cursor.execute("SELECT token FROM dbo.Login365 WHERE correo = ?", (correo,))
    row = Utils.cursor.fetchone()
    if not row or not row[0]:
        raise RuntimeError(f"No se encontró token activo en dbo.Login365 para {correo}.")
    return row[0]


def _obtener_pedidos_sin_guia() -> list[dict]:
    Utils.cursorLite.execute(
        """
        SELECT id, NumeroPedido, Transportadora, Ciudades, Departamento
        FROM InfoPedidos
        WHERE Guia IS NULL OR LENGTH(Guia) < 4
        ORDER BY id ASC
        """
    )
    rows = Utils.cursorLite.fetchall()
    headers = [col[0] for col in Utils.cursorLite.description]
    return [{headers[i]: row[i] for i in range(len(headers))} for row in rows]


def _crear_html_notificacion(fallos: list[dict]) -> str:
    filas_html = ""
    for item in fallos:
        filas_html += (
            "<tr>"
            f"<td>{item['NumeroPedido']}</td>"
            f"<td>{item['Transportadora'] or ''}</td>"
            f"<td>{item['Ciudades'] or ''}</td>"
            f"<td>{item['Departamento'] or ''}</td>"
            "</tr>"
        )

    return f"""
    <html>
      <body>
        <p>Buen día,</p>
        <p>Se detectaron pedidos sin guía creada. Por favor validar:</p>
        <table border="1" cellpadding="4" cellspacing="0">
          <thead>
            <tr>
              <th>Número Pedido</th>
              <th>Transportadora</th>
              <th>Ciudad</th>
              <th>Municipio/Departamento</th>
            </tr>
          </thead>
          <tbody>
            {filas_html}
          </tbody>
        </table>
        <p>Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
      </body>
    </html>
    """.strip()


def _enviar_por_graph(token: str, asunto: str, html: str, destinatarios: list[str]) -> None:
    to_recipients = [{"emailAddress": {"address": correo}} for correo in destinatarios]
    payload = {
        "message": {
            "subject": asunto,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": to_recipients,
        },
        "saveToSentItems": "true",
    }

    response = Utils.requests.post(
        GRAPH_SENDMAIL_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )

    if response.status_code >= 300:
        raise RuntimeError(f"Graph sendMail falló [{response.status_code}]: {response.text}")


def _enviar_por_smtp_oauth(token: str, asunto: str, html: str, destinatarios: list[str]) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = CORREO_365
    msg["To"] = ", ".join(destinatarios)
    msg.attach(MIMEText(html, "html", "utf-8"))

    auth_string = f"user={CORREO_365}\x01auth=Bearer {token}\x01\x01"
    auth_b64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as server:
        server.starttls()
        code, response = server.docmd("AUTH", "XOAUTH2 " + auth_b64)
        if code != 235:
            raise RuntimeError(f"Error SMTP AUTH XOAUTH2 [{code}]: {response}")
        server.sendmail(CORREO_365, destinatarios, msg.as_string())


def main() -> None:
    modo_prueba = _bool_env("NOTIFICAR_MODO_PRUEBA", default=False)
    forzar_reenvio = _bool_env("NOTIFICAR_FORZAR_REENVIO", default=False)
    destinatarios = _destinatarios_desde_env()

    pedidos = _obtener_pedidos_sin_guia()
    if not pedidos:
        print("No hay pedidos pendientes sin guía para notificar.")
        return

    estado_notificados = _cargar_estado_notificados()
    pendientes = pedidos if forzar_reenvio else [p for p in pedidos if str(p["NumeroPedido"]) not in estado_notificados]

    if not pendientes:
        print("No hay pedidos nuevos sin guía para notificar (sin duplicados).")
        return

    if modo_prueba:
        print("=== MODO PRUEBA ACTIVADO ===")
        print(f"Destinatarios de prueba: {', '.join(destinatarios)}")
        print(f"Pedidos detectados sin guía: {len(pendientes)}")
        for pedido in pendientes[:10]:
            print(
                f"- Pedido {pedido['NumeroPedido']} | "
                f"Transportadora: {pedido['Transportadora']} | "
                f"Ciudad: {pedido['Ciudades']} | "
                f"Municipio/Departamento: {pedido['Departamento']}"
            )
        print("No se envió correo ni se actualizó estado de notificados por estar en modo prueba.")
        return

    token = _obtener_token_login365(CORREO_365)
    asunto = f"[ALERTA] Pedidos sin guía ({len(pendientes)})"
    html = _crear_html_notificacion(pendientes)

    try:
        _enviar_por_graph(token, asunto, html, destinatarios)
        canal = "Graph API"
    except Exception as graph_error:
        print(f"Fallo envío por Graph API: {graph_error}")
        _enviar_por_smtp_oauth(token, asunto, html, destinatarios)
        canal = "SMTP OAuth2"

    for pedido in pendientes:
        estado_notificados.add(str(pedido["NumeroPedido"]))
    _guardar_estado_notificados(estado_notificados)

    print(
        f"Notificación enviada por {canal}. "
        f"Pedidos notificados: {len(pendientes)}. Destinatarios: {', '.join(destinatarios)}"
    )


if __name__ == "__main__":
    main()
