# 🛡️ Guardian API

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> API de alto rendimiento para gestión de guardianes y seguridad, diseñada con principios modernos de Platform Engineering.

## 📋 Descripción

Guardian API es un servicio backend robusto construido con **FastAPI** que gestiona la asignación y monitoreo de recursos de seguridad. El sistema está diseñado para ser escalable, resiliente y fácil de desplegar.

### ✨ Características Principales

- 🚀 **Alto Rendimiento**: API asíncrona construida sobre ASGI.
- 🐋 **Container-Native**: Entorno de desarrollo y producción 100% Dockerizado.
- 💾 **Persistencia Robusta**: PostgreSQL como fuente de verdad y Redis para caché de alto rendimiento.
- 🧪 **Testing Suite Complete**: Pruebas unitarias y de integración (usando Testcontainers).
- 📚 **Documentación Automática**: Swagger UI y ReDoc integrados.

---

## 🏗️ Arquitectura

Para ver detalles profundos sobre la arquitectura, diagramas de flujo y decisiones técnicas, consulta [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados.
- (Opcional) Make.

### 1. Clonar el repositorio

```bash
git clone https://github.com/benjacs-lan/guardian-api.git
cd guardian-api
```

### 2. Levantar servicios

```bash
docker compose up -d
```

La API estará disponible en `http://localhost:8080`.

### 3. Verificar estado

```bash
curl http://localhost:8080/health
# Respuesta esperada: {"status":"healthy","redis":"connected"}
```

---

## 🛠️ Desarrollo

### Ejecutar Tests

El proyecto incluye una suite de pruebas completa que corre dentro de Docker para asegurar consistencia.

```bash
# Tests Unitarios
docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c \
  "pip install -q -r requirements.txt -r requirements-dev.txt && pytest test/unit/ -v"

# Tests de Integración
docker run --rm -v $(pwd):/app -v /var/run/docker.sock:/var/run/docker.sock \
  -w /app --network guardian_network -e REDIS_HOST=redis python:3.12-slim bash -c \
  "pip install -q -r requirements.txt -r requirements-dev.txt && pytest test/integration/ -v"
```

---

## 📚 Documentación de API

Una vez levantado el servicio, puedes acceder a la documentación interactiva:

- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

---

## 📦 Estructura del Proyecto

```
guardian-api/
├── 📂 src/
│   └── 📂 app/             # Código fuente de la aplicación
│       ├── 📂 models/      # Modelos SQLAlchemy
│       ├── 📂 schemas/     # Esquemas Pydantic
│       ├── 📂 services/    # Lógica de negocio
│       └── main.py         # Punto de entrada FastAPI
├── 📂 test/                # Suite de pruebas con Pytest
├── compose.yml             # Orquestación de servicios
├── Dockerfile              # Definición de imagen multiplataforma
├── ARCHITECTURE.md         # Documentación de arquitectura técnica
└── requirements.txt        # Dependencias de producción
```

---

## 👤 Autor

Desarrollado con ❤️ por **[Benjamín](https://github.com/benjacs-lan)**.

---

_Este proyecto es parte de un portafolio de Platform Engineering & DevOps._
