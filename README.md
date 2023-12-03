# fastapi_clinic

Fastapi service with dogs database (demo available at https://fastapi-clinic-service-slavkostrov.onrender.com/).

Simple app run snippet:

```bash
uvicorn main:app --reload
```

There are several endpoints:
- `/ as` root endpoint with empty 200 answer;
- `/post` to store timestampt object;
- `/dog` for view/add dogs;
- `/dog/{pk}` for get dog with provided primary key or patch existing dog.

Also documentation available at `/docs` endpoint.

# Docker

To run container execute command:

```bash
sudo docker run -p 5555:5555 slavkostrov/clinic-app:latest
```

Authors:
- Kostrov Vyacheslav
