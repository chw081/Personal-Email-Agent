from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "OS is running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "email-agent"
    }