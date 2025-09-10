# BlogPost

Proyecto **BlogPost**, inspirado en el concurso **DevTalles 2025**.  
Este repositorio contiene la aplicación completa, dividida en **frontend** y **backend**, para la gestión de publicaciones, comentarios y likes en un blog.

---

## 📖 Descripción

BlogPost es una aplicación web que permite a los usuarios:

- Crear y gestionar publicaciones (posts).  
- Comentar y dar likes a las publicaciones.  
- Gestionar su perfil y autenticación de forma segura.  

El proyecto está pensado como **fullstack**, con **Next.js 15 + TypeScript + Sass** en el frontend y **Django Rest Framework** en el backend.  
Ambos servicios pueden ejecutarse de forma **dockerizada**, facilitando su despliegue y pruebas locales.

---

## 📂 Estructura del repositorio
```plaintext
blogpost/
├─ frontend/ # Aplicación Next.js 15
├─ backend/ # API con Django Rest Framework
├─ docker-compose.yml # Orquestación de contenedores
└─ README.md # Este archivo
```

---

## 🚀 Levantamiento del proyecto

1. Clonar el repositorio:  

```bash
git clone <url-del-repositorio>
cd blogpost
```
Levantar todos los servicios con Docker:

```bash
docker-compose up --build
```
- **Frontend:** [http://localhost:3000](http://localhost:3000)  
- **Backend:** [http://localhost:8000/api/](http://localhost:8000/api/)

---

## ⚙️ Stack Tecnológico

- **Frontend:** Next.js 15, TypeScript, SaSS
- **Backend:** Django 5, Django Rest Framework, PostgreSQL, JWT  
- **Infraestructura:** Docker + Docker Compose


# Requerimientos oficiales
* Landing page donde se puedan visualizar los posts.
* Filtros por categorías y buscador para los posts.
* Panel administrativo para la gestión de los posts (CRUD de posts,
solo personal admin puede acceder a todos los posts).
* Página para visualizar los detalles del post donde se pueda dar
"likes" y añadir comentarios al mismo. Un plus si se muestran
otros post de interés.
* Módulo para login y registro, se debe dar opción para iniciar
sesión al menos con Discord