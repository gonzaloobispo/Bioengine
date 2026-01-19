# drive_sync.py - Motor de Sincronización con Google Drive
import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import config

class DriveSyncManager:
    """
    Gestiona la sincronización recursiva de la carpeta maestra con Google Drive
    """
    def __init__(self):
        self.gauth = GoogleAuth()
        self.drive = None
        self.root_folder_name = "BioEngine_Master_Sync"
        self.local_root = config.SYNC_DATA
        
    def authenticate(self):
        """
        Autenticación robusta ( Soporta local y cloud )
        """
        try:
            # En local, busca client_secrets.json
            if os.path.exists('client_secrets.json'):
                self.gauth.LocalWebserverAuth()
            else:
                # En Cloud (Streamlit), intentaremos usar tokens guardados
                self.gauth.LoadCredentialsFile("mycreds.txt")
                if self.gauth.credentials is None:
                    # Esto fallará en cloud sin intervención, 
                    # pero es la base para el flujo de secrets.
                    print("[ERROR] No hay credenciales de Google Drive.")
                    return False
                elif self.gauth.access_token_expired:
                    self.gauth.Refresh()
                else:
                    self.gauth.Authorize()
            
            self.drive = GoogleDrive(self.gauth)
            return True
        except Exception as e:
            print(f"[ERROR] Autenticación Drive: {e}")
            return False

    def get_folder_id(self, folder_name, parent_id='root'):
        """Busca o crea una carpeta en Drive"""
        query = f"title = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        if file_list:
            return file_list[0]['id']
        
        # Crear si no existe
        folder = self.drive.CreateFile({
            'title': folder_name,
            'parents': [{'id': parent_id}],
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        return folder['id']

    def sync_recursive(self, local_path, drive_parent_id):
        """Sincroniza recursivamente local -> cloud"""
        for item in os.listdir(local_path):
            full_path = os.path.join(local_path, item)
            
            if os.path.isdir(full_path):
                # Es una subcarpeta
                drive_subfolder_id = self.get_folder_id(item, drive_parent_id)
                self.sync_recursive(full_path, drive_subfolder_id)
            else:
                # Es un archivo
                self.upload_file(full_path, drive_parent_id)

    def upload_file(self, local_file_path, drive_parent_id):
        """Sube un archivo si es más nuevo o no existe"""
        file_name = os.path.basename(local_file_path)
        query = f"title = '{file_name}' and '{drive_parent_id}' in parents and trashed = false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        
        if file_list:
            drive_file = file_list[0]
            # Podríamos comparar fechas aquí para ahorrar ancho de banda
            drive_file.SetContentFile(local_file_path)
            drive_file.Upload()
            print(f"   [SYNC] Actualizado: {file_name}")
        else:
            drive_file = self.drive.CreateFile({
                'title': file_name,
                'parents': [{'id': drive_parent_id}]
            })
            drive_file.SetContentFile(local_file_path)
            drive_file.Upload()
            print(f"   [SYNC] Subido: {file_name}")

    def download_recursive(self, drive_parent_id, local_path):
        """Descarga recursivamente cloud -> local"""
        if not os.path.exists(local_path):
            os.makedirs(local_path)
            
        file_list = self.drive.ListFile({'q': f"'{drive_parent_id}' in parents and trashed = false"}).GetList()
        for file in file_list:
            local_file_path = os.path.join(local_path, file['title'])
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.download_recursive(file['id'], local_file_path)
            else:
                # Descargar si no existe localmente
                if not os.path.exists(local_file_path):
                    file.GetContentFile(local_file_path)
                    print(f"   [SYNC] Descargado: {file['title']}")

    def full_sync_bidirectional(self):
        """Sincronización total: Sube lo nuevo, descarga lo que falta"""
        if not self.drive:
            if not self.authenticate(): return False
            
        print(f"[SYNC] Iniciando sincronizacion de {self.root_folder_name}...")
        root_id = self.get_folder_id(self.root_folder_name)
        
        # 1. Descargar lo que hay en nube y falta en local
        self.download_recursive(root_id, self.local_root)
        
        # 2. Subir lo que hay en local a la nube
        self.sync_recursive(self.local_root, root_id)
        
        # Guardar credenciales para no pedir login otra vez
        self.gauth.SaveCredentialsFile("mycreds.txt")
        
        print("DONE: Sincronizacion bidireccional completada.")
        return True

    def full_sync_to_cloud(self):
        """Alias para mantener compatibilidad"""
        return self.full_sync_bidirectional()

if __name__ == "__main__":
    sync = DriveSyncManager()
    sync.full_sync_to_cloud()
