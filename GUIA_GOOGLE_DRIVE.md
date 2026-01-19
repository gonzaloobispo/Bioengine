# Guía: Obtener Credenciales para Google Drive API

Para que tu Bio-Engine pueda subir archivos a tu Drive automáticamente, necesitamos crear un "pase de acceso" oficial de Google. Sigue estos pasos:

## 1. Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un **Nuevo Proyecto** (llámalo "BioEngineSync").
3. En el buscador superior, escribe **"Google Drive API"** y haz clic en **Habilitar**.

## 2. Pantalla de Consentimiento (OAuth Consent Screen)
1. En el menú lateral: **APIs y Servicios** > **Pantalla de consentimiento de OAuth**.
2. Selecciona **User Type: Externo**.
3. Rellena los datos obligatorios (Nombre: "BioEngine", tu email).
4. Dale a **Guardar y Continuar** hasta el final. No necesitas agregar alcances (scopes) manualmente, Python lo hará.
5. **IMPORTANTE:** En la pestaña "Usuarios de prueba", agrega **tu propio email de Gmail**.

## 3. Crear Credenciales
1. Menú lateral: **APIs y Servicios** > **Credenciales**.
2. Haz clic en **+ Crear Credenciales** > **ID de cliente de OAuth**.
3. Tipo de aplicación: **App de escritorio**.
4. Nombre: "BioEngine Client".
5. Haz clic en **Crear**.
6. Se abrirá una ventana. Haz clic en **DESCARGAR JSON**.

## 4. Activar en tu Bio-Engine
1. Cambia el nombre del archivo descargado a **`client_secrets.json`**.
2. Colócalo en la carpeta raíz de tu proyecto: `c:\BioEngine_Gonzalo\`.
3. Avisame cuando esté allí para que hagamos la primera sincronización.

---
**¿Por qué este lío?**
Google es muy estricto con la seguridad. Al hacer esto tú, el "dueño" de los datos eres tú y nadie más (ni siquiera la IA) tiene acceso a tu Drive fuera de lo que este script haga en esa carpeta específica.
