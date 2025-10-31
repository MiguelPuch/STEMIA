FROM public.ecr.aws/docker/library/python:3.12.7-slim  

#imagen desde la que se construye el contenedor

WORKDIR /app

#COPY .env /app/.env
COPY pyproject.toml /app/
COPY requirements.txt /app/

COPY chatbot /app/chatbot
COPY main.py /app/
COPY app.py /app/
COPY Classic_Fit.pdf /app/
COPY utils /app/utils
COPY public /app/public
COPY web /app/web
COPY .chainlit /app/.chainlit
COPY data /app/data


RUN pip install --no-cache-dir -r requirements.txt 
#dependencias

#puerto a usar

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

