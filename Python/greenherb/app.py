from fastapi import FastAPI
from greenherb.auth.controller import router as auth_router
from greenherb.auth.users_controller import router as users_router
from greenherb.herbs.controller import router as herbs_router
from greenherb.plans.controller import router as plans_router

app = FastAPI(title="GREENHERB API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(herbs_router)
app.include_router(plans_router)
