"""Detecta y normaliza correos existentes antes de crear el índice único."""

import argparse
import asyncio
from pathlib import Path
import sys

from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.security import EMAIL_UNIQUE_INDEX_OPTIONS, normalize_email


async def find_duplicate_emails(usuarios):
    """Agrupa cuentas cuyo correo solo difiere por espacios o mayúsculas."""
    pipeline = [
        {"$match": {"email": {"$type": "string"}}},
        {
            "$project": {
                "email": 1,
                "normalized_email": {"$toLower": {"$trim": {"input": "$email"}}},
            }
        },
        {
            "$group": {
                "_id": "$normalized_email",
                "users": {"$push": {"id": "$_id", "email": "$email", "rol": "$rol"}},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return [document async for document in usuarios.aggregate(pipeline)]


def print_duplicates(duplicates):
    for duplicate in duplicates:
        print(f"\nCorreo normalizado: {duplicate['_id']}")
        for user in duplicate["users"]:
            print(f"  - id={user['id']} | email={user['email']} | rol={user.get('rol', 'sin rol')}")


async def normalize_existing_emails(apply_changes: bool):
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    usuarios = client[settings.MONGODB_DB_NAME]["usuarios"]
    try:
        duplicates = await find_duplicate_emails(usuarios)
        if duplicates:
            print("Se encontraron cuentas duplicadas. No se modificó ningún dato:")
            print_duplicates(duplicates)
            print("\nConserva una cuenta por correo y migra sus datos relacionados antes de eliminar la otra.")
            return False

        pending_updates = []
        async for user in usuarios.find({"email": {"$type": "string"}}):
            normalized = normalize_email(user["email"])
            if normalized and normalized != user["email"]:
                pending_updates.append((user["_id"], normalized))

        print(f"No hay duplicados. Correos que se normalizarían: {len(pending_updates)}")
        if not apply_changes:
            print("Ejecuta de nuevo con --apply para aplicar los cambios y crear el índice único.")
            return True

        for user_id, email in pending_updates:
            await usuarios.update_one({"_id": user_id}, {"$set": {"email": email}})
        await usuarios.create_index("email", **EMAIL_UNIQUE_INDEX_OPTIONS)
        print("Correos normalizados e índice único sin distinción de mayúsculas creado.")
        return True
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Normaliza correos existentes de FonoApp.")
    parser.add_argument("--apply", action="store_true", help="Aplica los cambios tras confirmar que no hay duplicados.")
    args = parser.parse_args()
    success = asyncio.run(normalize_existing_emails(args.apply))
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()