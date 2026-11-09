FROM python:3.14-slim

WORKDIR /mqtt-bridge

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser
USER appuser

COPY . .

# ENV MQTT_HOST=localhost
# ENV MQTT_PORT=1883
# ENV MQTT_USERNAME=""
# ENV MQTT_PASSWORD=""
# ENV OSC_HOST=localhost
# ENV OSC_PORT=5000
# ENV MQTT_TOPICS=#

CMD [ "python", "mqtt2osc.py"]
