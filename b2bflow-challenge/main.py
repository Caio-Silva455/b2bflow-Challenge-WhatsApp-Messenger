import os
import logging
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")

    return create_client(url, key)


def fetch_contacts(client: Client, limit: int = 3) -> list[dict]:
    logger.info(f"Buscando até {limit} contato(s) no Supabase...")

    response = (
        client.table("contacts")
        .select("name, phone")
        .limit(limit)
        .execute()
    )

    contacts = response.data
    logger.info(f"{len(contacts)} contato(s) encontrado(s).")
    return contacts


def send_whatsapp_message(phone: str, message: str) -> bool:
    instance_id = os.getenv("ZAPI_INSTANCE_ID")
    token = os.getenv("ZAPI_TOKEN")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN")

    if not instance_id or not token:
        raise ValueError("ZAPI_INSTANCE_ID e ZAPI_TOKEN devem estar definidos no .env")

    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"

    headers = {
        "Content-Type": "application/json",
    }

    if client_token:
        headers["Client-Token"] = client_token

    payload = {
        "phone": phone,
        "message": message,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f"Mensagem enviada para {phone} — status {response.status_code}")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP ao enviar para {phone}: {e} — resposta: {response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao enviar para {phone}: {e}")
        return False


def build_message(name: str) -> str:
    return f"Olá, {name} tudo bem com você?"


def main():
    logger.info("=== Iniciando envio de mensagens b2bflow ===")

    try:
        client = get_supabase_client()
    except ValueError as e:
        logger.critical(f"Configuração inválida: {e}")
        return

    try:
        contacts = fetch_contacts(client, limit=3)
    except Exception as e:
        logger.critical(f"Erro ao buscar contatos no Supabase: {e}")
        return

    if not contacts:
        logger.warning("Nenhum contato encontrado. Encerrando.")
        return

    success_count = 0
    failure_count = 0

    for contact in contacts:
        name = contact.get("name", "").strip()
        phone = contact.get("phone", "").strip()

        if not name or not phone:
            logger.warning(f"Contato inválido (nome ou telefone ausente): {contact}")
            failure_count += 1
            continue

        message = build_message(name)
        logger.info(f"Enviando para {name} ({phone}): '{message}'")

        sent = send_whatsapp_message(phone, message)

        if sent:
            success_count += 1
        else:
            failure_count += 1

    logger.info(
        f"=== Concluído: {success_count} enviado(s), {failure_count} falha(s) ==="
    )


if __name__ == "__main__":
    main()