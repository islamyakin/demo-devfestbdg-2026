FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

RUN mkdir -p data && printf "Islam,Surabaya,Asoy\nIslamJuga,Bandung,GakAsoy\n" > data/customers.txt
CMD ["python3", "main.py"]
