FROM python:3.11

WORKDIR /code

# Upgrade pip
RUN pip install --upgrade pip

COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY app.yaml .

# Copy the entire repository; safer for CI when optional folders are absent
COPY . /code

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]d
