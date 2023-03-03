FROM python:3.8.10

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8061

CMD ["streamlit", "run", "Login_Page.py", "--server.port", "8061"]