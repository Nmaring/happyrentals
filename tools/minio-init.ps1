docker run --rm --entrypoint sh minio/mc:latest -c "mc alias set local http://host.docker.internal:9000 minioadmin minioadmin123 && mc mb --ignore-existing local/happyrentals-private && mc ls local"
