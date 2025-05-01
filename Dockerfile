FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && apt-get clean

WORKDIR /backend

COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir -r requirements.txt

COPY ./backend .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000" "--reload"]
