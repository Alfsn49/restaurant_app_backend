from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from io import BytesIO
import tempfile
import base64
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse, quote
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

# imagekit = ImageKit(
#     private_key=os.getenv("private_key"),
#     public_key=os.getenv("public_key"),
#     url_endpoint=os.getenv("url_endpoint")
# )

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_from_bytes(file_bytes: bytes, public_id: str, folder: str = None) -> str:
    """
    Sube una imagen a Cloudinary desde bytes
    """
    try:
        upload_options = {
            'public_id': public_id,
            'overwrite': True,
            'resource_type': 'image'
        }
        
        # Agregar folder si se especifica
        if folder:
            upload_options['folder'] = folder
        
        upload_result = cloudinary.uploader.upload(file_bytes, **upload_options)
        return upload_result['secure_url']
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload error: {str(e)}")

def delete_image_by_url(image_url: str) -> bool:
    """
    Elimina una imagen de Cloudinary usando su URL
    """
    try:
        if not image_url or "cloudinary.com" not in image_url:
            return False
            
        # Extraer public_id de la URL de Cloudinary (ahora incluye el folder)
        import re
        pattern = r'/image/upload/(?:v\d+/)?([^/]+)/([^/]+)\.(?:jpg|jpeg|png|gif|webp)'
        match = re.search(pattern, image_url)
        
        if match:
            folder_name = match.group(1)
            file_name = match.group(2)
            public_id = f"{folder_name}/{file_name}"
            
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        
        return False
        
    except Exception as e:
        print(f"Cloudinary delete error: {str(e)}")
        return False

# def upload_image_from_bytes(file_bytes: bytes, file_name: str, tags: list[str] = None) -> str:
#     """
#     Sube una imagen a ImageKit desde bytes usando el método upload()
#     """
#     try:
#         print(f"Starting upload for: {file_name}")
#         print(f"File size: {len(file_bytes)} bytes")
        
#         # Convertir bytes a base64
#         file_base64 = base64.b64encode(file_bytes).decode('utf-8')
#         print(f"Base64 length: {len(file_base64)} characters")
        
#         # Crear opciones de upload de forma más simple
#         options = UploadFileRequestOptions()
#         if tags:
#             options.tags = tags
        
#         # Hacer el upload con opciones mínimas
#         upload = imagekit.upload(
#             file=file_base64,
#             file_name=file_name,
#             options=options
#         )
        
#         print(f"Upload response: {upload}")
        
#         # Verificar si hay error
#         if hasattr(upload, 'error') and upload.error:
#             error_msg = upload.error.get('message', 'Unknown error')
#             raise RuntimeError(f"ImageKit error: {error_msg}")
        
#         # Obtener la URL
#         if hasattr(upload, 'url') and upload.url:
#             print(f"Upload successful! URL: {upload.url}")
#             return upload.url
#         elif hasattr(upload, 'response') and upload.response:
#             # Intentar obtener URL de la respuesta
#             response_data = upload.response
#             if isinstance(response_data, dict) and 'url' in response_data:
#                 return response_data['url']
        
#         raise RuntimeError("No URL returned from ImageKit upload")
        
#     except Exception as e:
#         print(f"Exception during upload: {str(e)}")
#         raise RuntimeError(f"Upload failed: {str(e)}")
    
# # Mantén la función original para compatibilidad
# def upload_image(file_path: str, file_name: str, tags: list[str] = None) -> str:
#     """
#     Sube una imagen desde una ruta de archivo (para backwards compatibility)
#     """
#     with open(file_path, 'rb') as file:
#         file_bytes = file.read()
#     return upload_image_from_bytes(file_bytes, file_name, tags)


# # ===== FUNCIONES DE ELIMINACIÓN CORREGIDAS =====

# def get_file_id_from_url(image_url: str) -> str:
#     """
#     Obtiene el fileId real de una imagen de ImageKit usando la API de metadata
#     """
#     try:
#         private_key = os.getenv("private_key")
#         if not private_key:
#             raise RuntimeError("ImageKit private key not configured")
        
#         # Extraer la ruta del archivo de la URL
#         parsed_url = urlparse(image_url)
#         path = parsed_url.path
        
#         # Codificar la ruta para la API de metadata
#         encoded_path = quote(path, safe='')
        
#         # API endpoint para obtener metadata
#         api_url = f"https://api.imagekit.io/v1/metadata{encoded_path}"
        
#         # Headers con autenticación
#         auth_string = f"{private_key}:"
#         encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
#         headers = {
#             'Authorization': f'Basic {encoded_auth}'
#         }
        
#         # Hacer la solicitud GET
#         response = requests.get(api_url, headers=headers)
        
#         print(f"Metadata API response status: {response.status_code}")
        
#         if response.status_code == 200:
#             metadata = response.json()
#             file_id = metadata.get('fileId')
#             if file_id:
#                 print(f"Found fileId: {file_id} for URL: {image_url}")
#                 return file_id
#             else:
#                 raise RuntimeError("No fileId found in metadata response")
#         else:
#             error_msg = response.text
#             raise RuntimeError(f"Metadata API error: HTTP {response.status_code} - {error_msg}")
            
#     except Exception as e:
#         print(f"Error getting fileId from metadata: {str(e)}")
#         raise RuntimeError(f"Cannot get fileId from URL: {str(e)}")

# def delete_image_by_file_id(file_id: str) -> bool:
#     """
#     Elimina una imagen usando el fileId
#     """
#     try:
#         print(f"Deleting image with fileId: {file_id}")
        
#         # Usar el método del SDK
#         delete_result = imagekit.delete_file(file_id=file_id)
        
#         # Verificar éxito
#         if hasattr(delete_result, 'error') and delete_result.error:
#             error_msg = delete_result.error.get('message', 'Unknown error')
#             # Si el archivo ya no existe, considerarlo como éxito
#             if "No file found" in error_msg or "not found" in error_msg.lower():
#                 print("File already deleted or not found")
#                 return True
#             else:
#                 raise RuntimeError(f"ImageKit delete error: {error_msg}")
        
#         print("Delete successful via SDK")
#         return True
            
#     except Exception as e:
#         print(f"Exception during SDK delete: {str(e)}")
#         # Intentar con API directa como fallback
#         return delete_image_direct_api(file_id)

# def delete_image_direct_api(file_id: str) -> bool:
#     """
#     Elimina una imagen usando la API directa
#     """
#     try:
#         private_key = os.getenv("private_key")
#         if not private_key:
#             raise RuntimeError("ImageKit private key not configured")
        
#         # API endpoint para eliminar
#         api_url = f"https://api.imagekit.io/v1/files/{file_id}"
        
#         # Headers con autenticación
#         auth_string = f"{private_key}:"
#         encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
#         headers = {
#             'Authorization': f'Basic {encoded_auth}'
#         }
        
#         # Hacer la solicitud DELETE
#         response = requests.delete(api_url, headers=headers)
        
#         print(f"Direct API delete response status: {response.status_code}")
        
#         if response.status_code == 204:  # 204 No Content = éxito
#             print("Delete successful via direct API")
#             return True
#         elif response.status_code == 404:
#             print("Image already deleted or not found")
#             return True
#         else:
#             error_msg = response.text
#             raise RuntimeError(f"Direct API error: HTTP {response.status_code} - {error_msg}")
            
#     except Exception as e:
#         print(f"Exception in direct API delete: {str(e)}")
#         raise RuntimeError(f"Direct API delete failed: {str(e)}")

# def delete_image_by_url_direct(image_url: str) -> bool:
#     """
#     Elimina una imagen usando solo la URL (método principal)
#     """
#     try:
#         print(f"Deleting image by URL: {image_url}")
        
#         # Paso 1: Obtener el fileId usando metadata API
#         file_id = get_file_id_from_url(image_url)
#         print(f"Obtained fileId: {file_id}")
        
#         # Paso 2: Eliminar usando el fileId
#         return delete_image_by_file_id(file_id)
        
#     except Exception as e:
#         print(f"Exception in delete by URL: {str(e)}")
#         raise RuntimeError(f"Delete by URL failed: {str(e)}")

# def extract_file_id_from_path(image_url: str) -> str:
#     """
#     Intenta extraer el fileId del path de la URL (método alternativo)
#     """
#     try:
#         from urllib.parse import urlparse
        
#         parsed_url = urlparse(image_url)
#         path = parsed_url.path
        
#         # Para URLs de ImageKit: https://ik.imagekit.io/endpoint/path/to/file.jpg
#         # El fileId es todo después del endpoint
#         parts = path.split('/')
        
#         if len(parts) >= 3:
#             # Tomar todo después del endpoint (partes[2] en adelante)
#             file_id = '/'.join(parts[2:])
#             print(f"Extracted fileId from path: {file_id}")
#             return file_id
#         else:
#             raise RuntimeError("Cannot extract fileId from URL path")
            
#     except Exception as e:
#         print(f"Error extracting fileId from path: {str(e)}")
#         raise RuntimeError(f"Cannot extract fileId from URL: {str(e)}")

# def delete_image_robust(image_url: str) -> bool:
#     """
#     Intenta eliminar una imagen usando múltiples métodos
#     """
#     # Primero verificar si la URL es de ImageKit
#     if "imagekit.io" not in image_url:
#         print("URL is not from ImageKit, skipping delete")
#         return True
    
#     methods = [
#         delete_image_by_url_direct,  # Método principal con metadata API
#         _delete_with_path_extraction, # Método alternativo
#     ]
    
#     for method in methods:
#         try:
#             print(f"Trying method: {method.__name__}")
#             if method(image_url):
#                 return True
#         except Exception as e:
#             print(f"Method {method.__name__} failed: {str(e)}")
#             continue
    
#     raise RuntimeError("All delete methods failed")

# def _delete_with_path_extraction(image_url: str) -> bool:
#     """
#     Método alternativo: extraer fileId del path y intentar eliminar
#     """
#     file_id = extract_file_id_from_path(image_url)
#     return delete_image_by_file_id(file_id)

# # Función principal para uso externo
# def delete_image_by_url(image_url: str) -> bool:
#     """
#     Elimina una imagen de ImageKit usando su URL (función principal)
#     """
#     try:
#         return delete_image_robust(image_url)
#     except Exception as e:
#         print(f"Error deleting image by URL: {str(e)}")
#         raise RuntimeError(f"Delete by URL failed: {str(e)}")

# # ===== FUNCIONES DE COMPATIBILIDAD =====

# def delete_image(file_id: str) -> bool:
#     """Función de compatibilidad"""
#     return delete_image_by_file_id(file_id)

# def delete_image_direct(file_id: str) -> bool:
    """Función de compatibilidad"""
    return delete_image_direct_api(file_id)