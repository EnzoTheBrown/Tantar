from .route import app
from .login import login_router
from .user import user_router
from .account import account_router
from .company import company_router
from .file import file_router
from .event import event_router
from .websocket import ws_router
from .graph import graph_router


app.include_router(login_router)
app.include_router(user_router)
app.include_router(account_router)
app.include_router(company_router)
app.include_router(file_router)
app.include_router(event_router)
app.include_router(ws_router)
app.include_router(graph_router)
