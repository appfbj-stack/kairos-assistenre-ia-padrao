"""
Seed script: creates the default tenant and admin user.
Run: python seed.py
"""
import asyncio
import uuid
from app.database import async_session, init_db, engine
from app.models import Base, Tenant
from sqlalchemy import select


async def seed():
    await init_db()
    async with async_session() as session:
        result = await session.execute(select(Tenant).where(Tenant.slug == "default"))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Tenant already exists: {existing.name} (key: {existing.api_key})")
            return

        api_key = f"kairos-{uuid.uuid4().hex[:24]}"
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Default",
            slug="default",
            api_key=api_key,
            context="Você é o Kairos, um assistente inteligente e amigável.",
        )
        session.add(tenant)
        await session.commit()
        print(f"Tenant created: {tenant.name}")
        print(f"API Key: {api_key}")


if __name__ == "__main__":
    asyncio.run(seed())
