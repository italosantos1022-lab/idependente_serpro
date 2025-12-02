from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os
import subprocess
import tempfile
import requests

AUTH_URL = "https://autenticacao.sapi.serpro.gov.br/authenticate"
BASIC_AUTH_HEADER = "Authorization:Basic aTlvbFZxeXJ0U0VYM04zNzNiU1Rpc1MxTjFvYTpJUUxWRmYwY3lPRTVUZmxnZldyWTd6ZE94Q0lh"
ROLE_HEADER = "Role-Type:TERCEIROS"
CONTENT_TYPE_HEADER = "Content-Type:application/x-www-form-urlencoded"

app = FastAPI()


class CertificateRequest(BaseModel):
    cert_url: str | None = None
    cert_password: str | None = None
    authorization: str | None = None


def download_certificate(url: str, destination: str) -> None:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(destination, "wb") as cert_file:
        for chunk in response.iter_content(chunk_size=8192):
            cert_file.write(chunk)


def build_curl_command(cert_path: str, cert_password: str, authorization: str) -> list[str]:
    return [
        "curl",
        "-s",
        "-i",
        "-X",
        "POST",
        "-H",
        f"Authorization:{authorization}",
        "-H",
        ROLE_HEADER,
        "-H",
        CONTENT_TYPE_HEADER,
        "-d",
        "grant_type=client_credentials",
        "--cert-type",
        "P12",
        "--cert",
        f"{cert_path}:{cert_password}",
        AUTH_URL,
    ]


@app.post("/authenticate", response_class=PlainTextResponse)
async def authenticate(payload: CertificateRequest) -> str:
    cert_url = payload.cert_url or os.getenv("CERT_URL")
    cert_password = payload.cert_password or os.getenv("CERT_PASSWORD", "")
    authorization = payload.authorization or os.getenv("AUTHORIZATION")

    if not cert_url:
        raise HTTPException(status_code=400, detail="Certificate URL is required")

    if not authorization:
        authorization = BASIC_AUTH_HEADER.split(":", 1)[1]

    with tempfile.TemporaryDirectory() as temp_dir:
        cert_path = os.path.join(temp_dir, "arquivo_certificado.p12")
        download_certificate(cert_url, cert_path)
        command = build_curl_command(cert_path, cert_password, authorization)
        process = subprocess.run(command, capture_output=True, text=True)
        return process.stdout or process.stderr
