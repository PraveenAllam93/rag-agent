from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import RoleModel, TenantModel, UserModel, UserTenantRoleModel
from .schemas import TenantCreateSchema, UserCreateSchema, UserUpdateSchema
from .security import hash_password


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(
        self,
        user: UserCreateSchema,
        tenant_id: int,
        role_id: int,
    ) -> UserModel:
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password),
        )
        self.db.add(db_user)
        await self.db.flush()

        db_user_tenant_role = UserTenantRoleModel(
            user_id=db_user.user_id,
            tenant_id=tenant_id,
            role_id=role_id,
        )
        self.db.add(db_user_tenant_role)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_user(self, user_id: int) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user: UserUpdateSchema) -> UserModel | None:
        db_user = await self.get_user(user_id)
        if not db_user:
            return None

        updates = user.model_dump(exclude_unset=True)
        password = updates.pop("password", None)
        if password is not None:
            db_user.password_hash = hash_password(password)
        for key, value in updates.items():
            setattr(db_user, key, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> UserModel | None:
        db_user = await self.get_user(user_id)
        if not db_user:
            return None
        await self.db.delete(db_user)
        await self.db.commit()
        return db_user

    async def get_all_users(self) -> list[UserModel]:
        result = await self.db.execute(select(UserModel))
        return list(result.scalars().all())


class TenantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(self, tenant: TenantCreateSchema) -> TenantModel:
        db_tenant = TenantModel(name=tenant.name)
        self.db.add(db_tenant)
        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def get_tenant(self, tenant_id: int) -> TenantModel | None:
        result = await self.db.execute(
            select(TenantModel).where(TenantModel.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_all_tenants(self) -> list[TenantModel]:
        result = await self.db.execute(select(TenantModel))
        return list(result.scalars().all())

    async def get_tenants_for_user(self, user_id: int):
        """Tenants + role a user belongs to. Used after password verification,
        before a tenant is chosen — never filter this by password here, a
        salted hash can't be matched with SQL equality."""
        result = await self.db.execute(
            select(TenantModel.tenant_id, TenantModel.name, UserTenantRoleModel.role_id)
            .join(UserTenantRoleModel, TenantModel.tenant_id == UserTenantRoleModel.tenant_id)
            .where(UserTenantRoleModel.user_id == user_id)
        )
        return result.all()


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role(self, role_id: int) -> RoleModel | None:
        result = await self.db.execute(select(RoleModel).where(RoleModel.role_id == role_id))
        return result.scalar_one_or_none()

    async def get_all_roles(self) -> list[RoleModel]:
        result = await self.db.execute(select(RoleModel))
        return list(result.scalars().all())

    async def get_roles_by_user_and_tenant(self, user_id: int, tenant_id: int) -> list[RoleModel]:
        result = await self.db.execute(
            select(RoleModel)
            .join(UserTenantRoleModel, RoleModel.role_id == UserTenantRoleModel.role_id)
            .where(
                UserTenantRoleModel.user_id == user_id,
                UserTenantRoleModel.tenant_id == tenant_id,
            )
        )
        return list(result.scalars().all())
