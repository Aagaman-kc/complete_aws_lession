from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()
BACKEND_URL = "http://backend-service:80"

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>K8s Production App</title></head>
    <body>
        <h1>Production‑grade Kubernetes App</h1>
        <div id="output">Loading...</div>
        <script>
            fetch('/api')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('output').innerHTML =
                        `<p><strong>Message:</strong> ${data.message}</p>
                         <p><strong>Time:</strong> ${data.time}</p>`;
                })
                .catch(err => {
                    document.getElementById('output').innerText = 'Error: ' + err;
                });
        </script>
    </body>
    </html>
    """

@app.get("/api")
async def proxy_api():
    async with httpx.AsyncClient() as client:
        resp = await client.get(BACKEND_URL)
        return resp.json()
