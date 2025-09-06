FROM python:3.9-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./shared /code/shared
COPY ./order_service/app /code/app
CMD ["coverage", "run", "--parallel-mode", "--source=app", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]