from fastapi import FastAPI

app = FastAPI(title="Sistema de Donaciones de Alimentos", version="1.0")


@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
