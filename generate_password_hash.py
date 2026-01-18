import streamlit_authenticator as stauth

# Script para generar hash de contraseña
# Correr esto una vez para obtener el hash

password = input("Ingresa la contraseña que quieres usar: ")

# Usar la API correcta de streamlit-authenticator
hasher = stauth.Hasher()
hashed = hasher.hash(password)

print("\n" + "="*50)
print("HASH GENERADO (Copia esto):")
print("="*50)
print(hashed)
print("="*50)
print("\nInstrucciones:")
print("1. Copia el hash de arriba")
print("2. En Streamlit Cloud, ve a Settings > Secrets")
print("3. Agrega:")
print(f"""
GEMINI_API_KEY = "TU_API_KEY_REAL"

[credentials.usernames.gonzalo]
name = "Gonzalo Obispo"
password = "{hashed}"
""")
