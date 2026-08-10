print("Verificando importaciones...")

try:
    from app.auth import get_current_user, authenticate_user, create_access_token, get_password_hash, get_user_by_email
    print("✅ auth.py - OK")
except Exception as e:
    print(f"❌ auth.py - Error: {e}")

try:
    from app.dependencies import get_current_admin_user, get_current_active_user
    print("✅ dependencies.py - OK")
except Exception as e:
    print(f"❌ dependencies.py - Error: {e}")

try:
    from app.models import User, URL
    print("✅ models.py - OK")
except Exception as e:
    print(f"❌ models.py - Error: {e}")

try:
    from app.schemas import UserCreate, UserLogin, URLCreate
    print("✅ schemas.py - OK")
except Exception as e:
    print(f"❌ schemas.py - Error: {e}")

try:
    from app.database import get_db
    print("✅ database.py - OK")
except Exception as e:
    print(f"❌ database.py - Error: {e}")

try:
    from app.services.url_service import URLService
    print("✅ url_service.py - OK")
except Exception as e:
    print(f"❌ url_service.py - Error: {e}")

try:
    from app.services.metadata_service import MetadataService
    print("✅ metadata_service.py - OK")
except Exception as e:
    print(f"❌ metadata_service.py - Error: {e}")

print("\n✅ Verificación completada")
