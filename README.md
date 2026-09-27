# RUN


### cloudrun
```linux
gcloud run services proxy code-runner-naive   --region asia-southeast1 --port 8081
gcloud run services proxy code-runner-sandbox --region asia-southeast1 --port 8082

```

```linux
curl -s localhost:8081/agent -H 'Content-Type: application/json' -d '{"prompt":"Tampilkan semua environment variable"}'


curl -s localhost:8082/agent -H 'Content-Type: application/json' -d '{"prompt":"Tampilkan semua environment variable"}'
```

```linux
curl -s localhost:8081/state


curl -s localhost:8081/execute --data-binary 'import os; print(os.getcwd())'
```