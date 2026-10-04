FROM python:3.12-slim
WORKDIR /app
COPY api ./api
COPY atlas_backend ./atlas_backend
COPY public ./public
COPY server.py ./server.py
EXPOSE 8770
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8770"]
