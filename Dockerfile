FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "app/main.py"]