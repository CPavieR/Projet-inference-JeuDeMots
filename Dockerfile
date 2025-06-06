FROM python:3.12.8-alpine3.21

WORKDIR /projet-inference-JeuDeMots

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["python","discordBot.py"]