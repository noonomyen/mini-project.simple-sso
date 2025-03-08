FROM python:3.12-slim

WORKDIR /app

COPY simple_sso /app/simple_sso
COPY tools /app/tools
COPY .env /app/.env
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Handcode the secret key and database uri
RUN echo "SECRET_KEY=\"GzS0Pz2othuFZUVeVaeVHi00arMe4bXi\"" > /app/.env && \
    echo "SQLALCHEMY_DATABASE_URI=\"sqlite:////app/db.sqlite\"" >> /app/.env

RUN python -m simple_sso --init-db
RUN python /app/tools/exec-sqlite.py /app/db.sqlite "INSERT INTO user (username, full_name, email, password, registered_at) VALUES ('admin', 'Admin', 'admin@localhost', '\$2b\$12\$0ZNAQoqHH2YXPwohcXVS/ucp0tVRDt6J0/UNMFf90W/tToPghjTru', '2025-01-01 00:00:00.000000')"

EXPOSE 5000

CMD ["python", "-m", "simple_sso"]
