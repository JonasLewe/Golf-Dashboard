FROM python:3.9

WORKDIR /

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "streamlit", "run", "golf_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

