import asyncio
from datetime import datetime
import jwt

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import select

from tantar.utils.logger import get_logger
from tantar.settings import SETTINGS
from schemas.relational import User
from tantar.database import get_db, Session
from schemas.websocket import WebSocketMessage
from .authenticate import ALGORITHM

logger = get_logger(__name__)
ws_router = APIRouter()

websocket_connections: dict[str, list[WebSocket]] = {}


def remove_websocket_connection(account_id: str, websocket: WebSocket):
    """Remove a websocket from the account's connection list.
    If there are no remaining connections for that account, the account is removed
    from the mapping.
    """
    if account_id in websocket_connections:
        try:
            websocket_connections[account_id].remove(websocket)
            if not websocket_connections[account_id]:
                del websocket_connections[account_id]
        except ValueError:
            pass


@ws_router.websocket("/ws/{token}")
async def websocket_endpoint_account(token: str, websocket: WebSocket):
    await websocket.accept()

    try:
        account_id = jwt.decode(token, SETTINGS.app.secret, algorithms=[ALGORITHM]).get(
            "account_id"
        )
    except Exception as e:
        logger.info(f"Error during websocket connection setup: {e}")
        await websocket.close()
        return

    if account_id in websocket_connections:
        websocket_connections[account_id].append(websocket)
    else:
        websocket_connections[account_id] = [websocket]

    try:
        for _ in range(1000):
            await websocket.receive_text()
            await asyncio.sleep(10)
            payload = jwt.decode(token, SETTINGS.app.secret, algorithms=[ALGORITHM])
            if datetime.now().timestamp() > payload.get("exp", 0):
                remove_websocket_connection(account_id, websocket)
                await websocket.close()
                break
        remove_websocket_connection(account_id, websocket)
    except WebSocketDisconnect:
        remove_websocket_connection(account_id, websocket)
    except Exception as e:
        logger.error(f"Error in websocket connection for account {account_id}: {e}")
        remove_websocket_connection(account_id, websocket)


@ws_router.post("/ws/notify/{company_id}")
async def notify_company(
    company_id: str, message: WebSocketMessage, db: Session = Depends(get_db)
):
    await notify(company_id, message, db)


async def notify(company_id: str, message: WebSocketMessage, db: Session):
    """
    Send event updates to all WebSocket clients connected to the specified company.
    Iterates over all accounts that have an active websocket connection and,
    after verifying the account is associated with the given company,
    sends the message to each connection.
    """
    logger.info(f"Notifying clients for company {company_id} with message: {message}")

    for account_id, websockets in list(websocket_connections.items()):
        user = db.exec(select(User).where(User.original_id == account_id)).first()
        if not user:
            continue

        company_ids = [str(company.original_id) for company in user.companies]
        if company_id in company_ids:
            logger.info(
                f"Sending data to client for company {company_id} (account {account_id})"
            )
            for websocket in websockets:
                try:
                    await websocket.send_json(message.model_dump())
                except Exception as e:
                    logger.error(
                        f"Failed to send data to client for company {company_id} (account {account_id}): {e}"
                    )
                    remove_websocket_connection(account_id, websocket)


async def notify_account(account_id: str, message: WebSocketMessage):
    """
    Send event updates to all WebSocket clients connected to the specified company.
    Iterates over all accounts that have an active websocket connection and,
    after verifying the account is associated with the given company,
    sends the message to each connection.
    """
    logger.info(f"Notifying clients for account {account_id} with message: {message}")
    websockets = websocket_connections.get(account_id, [])
    for websocket in websockets:
        try:
            await websocket.send_json(message.model_dump())
        except Exception as e:
            logger.error(f"Failed to send data to client (account {account_id}): {e}")
            remove_websocket_connection(account_id, websocket)
