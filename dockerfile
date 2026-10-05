FROM python:3.9

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sumo \
    sumo-tools \
    sumo-doc 

RUN pip install eclipse-sumo==1.27.0
RUN pip install --upgrade traci sumolib
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/simulation_files

ENV SUMO_HOME="/usr/share/sumo"

ENTRYPOINT ["python3", "main_1.py"]