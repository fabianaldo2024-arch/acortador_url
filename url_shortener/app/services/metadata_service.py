import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.url_service import URLService

class MetadataService:
    @staticmethod
    async def fetch_metadata(url: str) -> Dict[str, Optional[str]]:
        """Scrapea título, descripción e imagen de una URL"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Título
                title = soup.title.string if soup.title else None
                if not title:
                    og_title = soup.find('meta', attrs={'property': 'og:title'})
                    if og_title:
                        title = og_title.get('content')
                
                # Descripción
                description = None
                desc_meta = soup.find('meta', attrs={'name': 'description'})
                if desc_meta:
                    description = desc_meta.get('content')
                else:
                    og_desc = soup.find('meta', attrs={'property': 'og:description'})
                    if og_desc:
                        description = og_desc.get('content')
                
                # Imagen
                image_url = None
                og_image = soup.find('meta', attrs={'property': 'og:image'})
                if og_image:
                    image_url = og_image.get('content')
                
                return {
                    "title": title or "Sin título",
                    "description": description or "Sin descripción",
                    "image_url": image_url
                }
        except Exception as e:
            print(f"Error al obtener metadata: {e}")
            return {"title": "Error al cargar", "description": "No se pudo obtener metadata", "image_url": None}
    
    @staticmethod
    async def fetch_and_save_metadata(db: AsyncSession, url_id: int, original_url: str):
        """Obtiene metadata y la guarda en la base de datos"""
        metadata = await MetadataService.fetch_metadata(original_url)
        await URLService.update_url_metadata(
            db, 
            url_id, 
            metadata["title"], 
            metadata["description"], 
            metadata["image_url"]
        )
