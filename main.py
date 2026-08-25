from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import auth_router

app = FastAPI(title="UdharrDe")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if directory exists
# if os.path.exists("static"):
#     app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"messages" : "API is Running perfectly."}

