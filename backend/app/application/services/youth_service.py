"""Youth Management Service"""
from uuid import uuid4
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.repositories.youth_repository import YouthRepository, get_youth_repository
from app.infrastructure.repositories.branch_repository import BranchRepository, get_branch_repository
from app.infrastructure.database.models.youth import YouthModel
from app.domain.value_objects.enums import Gender, MembershipStatus


class YouthService:
    def __init__(
        self,
        youth_repo: YouthRepository = Depends(get_youth_repository),
        branch_repo: BranchRepository = Depends(get_branch_repository)
    ):
        self.youth_repo = youth_repo
        self.branch_repo = branch_repo
    
    async def create_youth(
        self, fullname: str, branch_id: str, gender: Gender,
        email: str | None, phone: str | None, department_id: str | None,
        date_of_birth: str | None, db: AsyncSession
    ) -> YouthModel:
        # Validate branch
        branch = await self.branch_repo.get_by_id(branch_id, db)
        if not branch:
            raise NotFoundException(f"Branch {branch_id} not found")
        
        youth = YouthModel(
            id=str(uuid4()), fullname=fullname, branch_id=branch_id,
            gender=gender, email=email, phone=phone,
            department_id=department_id, membership_status=MembershipStatus.ACTIVE
        )
        return await self.youth_repo.save(youth, db)
    
    async def get_youth(self, youth_id: str, db: AsyncSession) -> YouthModel:
        youth = await self.youth_repo.get_by_id(youth_id, db)
        if not youth:
            raise NotFoundException(f"Youth {youth_id} not found")
        return youth
    
    async def list_youths(
        self, branch_id: str, offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        return await self.youth_repo.list_by_branch(branch_id, offset, limit, db)
    
    async def search_youths(
        self, query: str, branch_id: str | None,
        offset: int, limit: int, db: AsyncSession
    ) -> tuple[list[YouthModel], int]:
        return await self.youth_repo.search(query, branch_id, offset, limit, db)
    
    async def update_youth(
        self, youth_id: str, updates: dict, db: AsyncSession
    ) -> YouthModel:
        youth = await self.get_youth(youth_id, db)
        for key, value in updates.items():
            if hasattr(youth, key):
                setattr(youth, key, value)
        return await self.youth_repo.save(youth, db)
    
    async def delete_youth(self, youth_id: str, db: AsyncSession) -> bool:
        return await self.youth_repo.delete(youth_id, db)
    
    async def upload_avatar(
        self, youth_id: str, file: UploadFile, db: AsyncSession
    ) -> str:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise ValidationException("File must be an image")
        # Placeholder - actual implementation would upload to storage
        avatar_url = f"/uploads/avatars/{youth_id}.jpg"
        await self.youth_repo.update_avatar(youth_id, avatar_url, db)
        return avatar_url
    
    async def get_attendance_summary(
        self, youth_id: str, limit: int, db: AsyncSession
    ) -> list[dict]:
        return await self.youth_repo.get_attendance_history(youth_id, limit, db)


def get_youth_service(
    youth_repo: YouthRepository = Depends(get_youth_repository),
    branch_repo: BranchRepository = Depends(get_branch_repository)
) -> YouthService:
    return YouthService(youth_repo, branch_repo)
