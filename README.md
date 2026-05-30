# Simulador Financiero - Compra Inteligente Vehicular 🚗💰

Sistema web desarrollado para implementar y simular un plan de pagos vehicular bajo el método francés vencido ordinario, utilizando la modalidad de **Compra Inteligente** dentro del contexto del Sistema Financiero Peruano.

El proyecto permite calcular cronogramas de pago, indicadores financieros y gestionar configuraciones adaptadas a entidades financieras peruanas.

---

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- Inicio de sesión obligatorio mediante Login y Password.
- Gestión segura de accesos y sesiones.

### 👥 Gestión de Roles y Permisos
Control granular de usuarios:
- Sin Acceso
- Solo Lectura (Read)
- Lectura y Escritura (Read & Write)
- Acceso Total

### 💱 Configuración Financiera Flexible
- Soporte para Soles (PEN) y Dólares (USD).
- Tasas Nominales y Efectivas.
- Configuración de capitalización.
- Periodos de gracia:
  - Total
  - Parcial

### 📊 Indicadores Financieros
Cálculo automático de:
- TCEA
- Flujo de Caja
- VAN
- TIR
- Cronograma de pagos

### 🚘 Gestión Vehicular y Clientes
- Registro de clientes.
- Registro de vehículos.
- Edición y actualización de información financiera.

---

## 🛠️ Tech Stack

### Backend
- Django 5.x
- Python 3.x

### Frontend
- HTML5
- Tailwind CSS
- JavaScript

### Base de Datos
- PostgreSQL
- SQLite (desarrollo)

---

## 📂 Estructura del Proyecto

```bash
project/
│
├── backend/
├── frontend/
├── static/
├── templates/
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación y Ejecución

### 1️⃣ Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

### 2️⃣ Crear entorno virtual

```bash
python -m venv venv
```

### 3️⃣ Activar entorno virtual

#### Windows
```bash
venv\Scripts\activate
```

#### Linux / Mac
```bash
source venv/bin/activate
```

### 4️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5️⃣ Ejecutar migraciones

```bash
python manage.py migrate
```

### 6️⃣ Iniciar servidor

```bash
python manage.py runserver
```

---

## 📸 Capturas del Sistema

> Aquí pueden agregar imágenes del login, simulador financiero, cronograma, dashboard, etc.

---

## 📌 Objetivo Académico

Proyecto desarrollado para el curso:

- **Curso:** SI642 - Finanzas e Ingeniería Económica
- **Institución:** Universidad Peruana de Ciencias Aplicadas (UPC)

El sistema busca aplicar principios de ingeniería económica y desarrollo de software para resolver problemas financieros relacionados al crédito vehicular. :contentReference[oaicite:2]{index=2}

---

## 👨‍💻 Autores

- Arthur Vincent De La Cruz Ramirez
- Integrantes del grupo

---

## 📄 Licencia

Este proyecto utiliza la licencia MIT.
