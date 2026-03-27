# enable mcron

enable-rcon=true
rcon.port=25575
rcon.password=YOUR_STRONG_PASSWORD


# uvicorn

python -m uvicorn app:app --host 127.0.0.1 --port 8050