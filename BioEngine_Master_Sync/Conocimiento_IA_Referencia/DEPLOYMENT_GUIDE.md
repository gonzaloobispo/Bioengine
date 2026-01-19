# Guía de Deployment: BioEngine a Streamlit Cloud

## Paso 1: Generar Hash de Contraseña

```bash
pip install streamlit-authenticator
python generate_password_hash.py
```

Copia el hash generado.

## Paso 2: Subir a GitHub

```bash
# Verificar que secrets.json NO se suba
git status

# Agregar cambios
git add .
git commit -m "add: Authentication system and cloud deployment files"
git push origin master
```

## Paso 3: Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Login con GitHub
3. Click "New app"
4. Selecciona:
   - Repository: `tu-usuario/BioEngine_Gonzalo`
   - Branch: `master`
   - Main file: `dashboard.py`

5. Click "Advanced settings"
6. En "Secrets", pega:

```toml
GEMINI_API_KEY = "TU_API_KEY_REAL"

[credentials.usernames.gonzalo]
name = "Gonzalo Obispo"
password = "EL_HASH_QUE_GENERASTE"
```

7. Click "Deploy"

## Paso 4: Acceso desde iPhone

La URL será: `https://bioenginegonzalo-2r498ml3ub6fncsjt3grdy.streamlit.app/`

### Agregar a Home Screen:
1. Abre Safari en iPhone
2. Ve a la URL
3. Tap botón "Compartir" (cuadrado con flecha)
4. "Añadir a pantalla de inicio"
5. ¡Listo! Ahora tienes un ícono como app nativa

---

## Notas Importantes:

- ⚠️ Los datos en `data_processed/` NO se suben (muy grandes). El dashboard mostrará error al inicio.
- ✅ Una vez en la nube, sube manualmente un CSV de prueba pequeño o ajusta el código para ignorar archivos faltantes.
- 🔒 Tu contraseña está hasheada, nunca se guarda en texto plano.
