# BlogPost — Frontend

Frontend del proyecto **BlogPost**, construido con **Next.js 15** y **TypeScript**.  
Provee la interfaz de usuario para la gestión de posts, comentarios y likes, consumiendo la API del backend.  
Se distribuye como aplicación **dockerizada** para facilitar la ejecución en cualquier entorno.



## 📖 Descripción

Este frontend está desarrollado con el **App Router de Next.js**.  
Incluye autenticación de usuarios, creación de publicaciones, comentarios y sistema de likes.  
La interfaz está construida con **TailwindCSS** y componentes de **shadcn/ui**, ofreciendo un diseño moderno y responsivo.



## ⚙️ Stack Tecnológico

- **Next.js 15 (App Router)**
- **React 18**
- **TypeScript**
- **SaSS**
- **Axios** para consumo de API
- **Jest + React Testing Library** para testing


El frontend estará disponible en:  
👉 [http://localhost:3000](http://localhost:3000)

## 🗂️ Estructura de carpetas

```plaintext
frontend/
│── app/                # Rutas y páginas (App Router)
│   ├── layout.tsx      # Layout principal
│   ├── page.tsx        # Home (feed de posts)
│   ├── auth/           # Registro e inicio de sesión
│   ├── posts/          # CRUD de posts
│   ├── comments/       # Gestión de comentarios
│   └── profile/        # Perfil de usuario
│
│── components/         # Componentes reutilizables (UI, formularios, etc.)
│── lib/                # Configuración de API, utilidades
│── styles/             # Estilos globales
│── public/             # Recursos estáticos (imágenes, íconos)
│── tests/              # Tests unitarios y de integración
```

## 🌐 Rutas principales
- `/` → Página principal (feed de posts)
- `/auth/login` → Inicio de sesión
- `/auth/register` → Registro de usuario
- `/posts/[id]` → Detalle de un post con comentarios
- `/profile/[username]` → Perfil del usuario
