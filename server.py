import json
import mimetypes
import os
import sys
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from google import genai
from google.genai import types


APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"
MODEL_NAME = "gemini-flash-lite-latest"


class ApiError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(detail)


def get_api_key() -> str:
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    secrets_path = APP_DIR / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        return ""

    try:
        data = tomllib.loads(secrets_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return ""

    return str(data.get("GEMINI_API_KEY", "")).strip()


def generate(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key:
        raise ApiError(
            503,
            "Configure GEMINI_API_KEY em .streamlit/secrets.toml ou nas variáveis de ambiente.",
        )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000),
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except Exception as exc:
        raise ApiError(
            502,
            "Não consegui falar com a IA agora. Confira a chave da API e tente novamente.",
        ) from exc

    return response.text or "Não consegui gerar uma resposta agora."


def ask_response(payload: dict) -> dict[str, str]:
    question = str(payload.get("message", "")).strip()
    if not question:
        raise ApiError(400, "Digite uma pergunta antes de enviar.")

    answer = generate(
        f"""
        Você é o QuimIA, um assistente virtual especializado em química para alunos do ensino médio.

        Responda com:
        - linguagem simples e acolhedora;
        - explicação passo a passo;
        - analogia do cotidiano quando ajudar;
        - fórmulas importantes em destaque;
        - um mini resumo final em até 3 tópicos.

        Pergunta do aluno:
        {question}
        """
    )
    return {"answer": answer}


def summary_response(payload: dict) -> dict[str, str]:
    topic = str(payload.get("topic", "")).strip()
    topic_line = f"sobre {topic}" if topic else "sobre um tema importante de química do ensino médio"

    answer = generate(
        f"""
        Crie um Resumo de 5 minutos {topic_line} para alunos do ensino médio.

        Estruture assim:
        1. Ideia central em linguagem simples.
        2. Exemplo cotidiano.
        3. Fórmula, regra ou conceito-chave.
        4. Erro comum que o aluno deve evitar.
        5. Três pontos para memorizar antes da prova.

        Seja direto, didático e motivador.
        """
    )
    return {"answer": answer}


def question_response(payload: dict) -> dict[str, str]:
    topic = str(payload.get("topic", "")).strip()
    style = str(payload.get("style", "regular")).strip()
    topic_line = f" sobre {topic}" if topic else ""

    if style == "enem":
        prompt = f"""
        Crie uma questão de química no estilo ENEM{topic_line}.

        Requisitos:
        - contexto cotidiano ou problema social;
        - enunciado claro;
        - 5 alternativas de A a E;
        - resposta correta;
        - resolução comentada passo a passo;
        - dica final de como reconhecer esse tipo de questão.
        """
    else:
        prompt = f"""
        Gere uma questão objetiva de química para ensino médio{topic_line}.

        Requisitos:
        - enunciado contextualizado;
        - 4 alternativas;
        - resposta correta;
        - explicação detalhada;
        - revisão curta do conceito cobrado.
        """

    return {"answer": generate(prompt)}


class QuimiaHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), format % args))

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            self.send_file(STATIC_DIR / "index.html")
            return

        if path == "/api/health":
            self.send_json({"ok": True, "has_api_key": bool(get_api_key())})
            return

        if path == "/logo-horizontal.png":
            logo_path = APP_DIR / "logo-horizontal.png"
            self.send_file(logo_path if logo_path.exists() else APP_DIR / "logo.png")
            return

        if path.startswith("/static/"):
            relative = path.removeprefix("/static/")
            file_path = (STATIC_DIR / relative).resolve()
            if STATIC_DIR.resolve() in file_path.parents and file_path.exists():
                self.send_file(file_path)
                return

        self.send_json({"detail": "Rota não encontrada."}, status=404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        try:
            payload = self.read_json()

            if path == "/api/ask":
                self.send_json(ask_response(payload))
            elif path == "/api/summary":
                self.send_json(summary_response(payload))
            elif path == "/api/question":
                self.send_json(question_response(payload))
            else:
                self.send_json({"detail": "Rota não encontrada."}, status=404)
        except ApiError as exc:
            self.send_json({"detail": exc.detail}, status=exc.status)
        except json.JSONDecodeError:
            self.send_json({"detail": "JSON inválido."}, status=400)
        except Exception:
            self.send_json({"detail": "Erro inesperado no servidor."}, status=500)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        if not path.exists():
            self.send_json({"detail": "Arquivo não encontrado."}, status=404)
            return

        content = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = ThreadingHTTPServer(("127.0.0.1", port), QuimiaHandler)
    print(f"QuimIA rodando em http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
