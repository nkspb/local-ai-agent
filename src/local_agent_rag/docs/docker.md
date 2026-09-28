# Docker

## Images and containers

A Docker image is a read-only template made of stacked filesystem layers. A container is a running instance of an image with a thin writable layer on top. Many containers can run from the same image, and changes made inside a container are lost when it is removed unless they are written to a volume.

Useful commands:

- `docker build -t myapp:1.0 .` builds an image from the Dockerfile in the current directory.
- `docker run -d -p 8080:80 myapp:1.0` runs a container in the background and maps host port 8080 to container port 80.
- `docker ps -a` lists all containers, including stopped ones.
- `docker logs -f <container>` streams container logs.
- `docker exec -it <container> sh` opens a shell inside a running container.

## Dockerfile basics

Each instruction in a Dockerfile creates a layer. Docker caches layers and reuses them when the instruction and its inputs have not changed. To get the most from the cache, put instructions that change rarely (installing dependencies) before instructions that change often (copying source code).

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER 1000
CMD ["python", "main.py"]
```

`CMD` sets the default command, which can be overridden at `docker run`. `ENTRYPOINT` sets the executable that always runs; arguments passed to `docker run` are appended to it.

## Multi-stage builds

Multi-stage builds use several `FROM` statements in one Dockerfile. You compile or build in a large builder image, then copy only the resulting artifacts into a small runtime image. This keeps build tools out of the final image and shrinks its size.

```dockerfile
FROM golang:1.23 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/server .

FROM gcr.io/distroless/static
COPY --from=builder /out/server /server
ENTRYPOINT ["/server"]
```

## Volumes and bind mounts

- **Named volumes** are managed by Docker and stored under Docker's data directory. They are the preferred way to persist database data.
- **Bind mounts** map a specific host path into the container. They are handy in development for live code reloading.
- **tmpfs mounts** live only in memory and disappear when the container stops.

## Docker networking

By default, containers attach to the `bridge` network. On a user-defined bridge network, containers can reach each other by container name through Docker's embedded DNS server. On the default bridge network they can only reach each other by IP address. The `host` network mode removes network isolation and shares the host's network stack.

## Docker Compose

Docker Compose defines multi-container applications in a `compose.yaml` file. `docker compose up -d` starts all services, and `docker compose down` stops and removes them. Compose creates a dedicated network for the project automatically, so services can reach each other by service name.

## Image security

- Use small base images (slim, alpine, or distroless) to reduce the attack surface.
- Run as a non-root user with the `USER` instruction.
- Pin base image versions instead of using `latest`.
- Scan images for known vulnerabilities with tools such as Trivy or Docker Scout.
- Never bake secrets into image layers; they remain in the image history even if deleted in a later layer.

## Team conventions

These are the internal conventions for our images:

- All images are pushed to the internal registry at `registry.internal.example:5000`.
- Image tags use the format `<service>:<git-short-sha>`; the `latest` tag is forbidden in production.
- The approved Python base image is `python:3.12-slim`; the approved Go runtime image is `gcr.io/distroless/static`.
- CI fails the build if Trivy reports any vulnerability of severity HIGH or CRITICAL.
