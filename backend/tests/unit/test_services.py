"""Service Layer Unit Tests"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.services.branch_service import BranchService
from app.application.services.youth_service import YouthService
from app.infrastructure.database.models.branch import BranchModel
from app.infrastructure.database.models.youth import YouthModel
from app.core.exceptions import NotFoundException, ValidationException


@pytest.mark.asyncio
async def test_branch_service_create_branch():
    """Test creating a branch"""
    mock_repo = AsyncMock()
    service = BranchService(branch_repo=mock_repo, user_repo=AsyncMock())
    
    # Mock no existing branch
    mock_repo.find_by_name.return_value = None
    
    # Mock save
    mock_branch = BranchModel(id="new-branch", name="New Branch", location="New City")
    mock_repo.save.return_value = mock_branch
    
    # Test
    db = AsyncMock()
    result = await service.create_branch("New Branch", "New City", None, None, None, db)
    
    assert result.name == "New Branch"
    mock_repo.find_by_name.assert_called_once()
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_branch_service_create_duplicate_name():
    """Test creating branch with duplicate name raises exception"""
    mock_repo = AsyncMock()
    service = BranchService(branch_repo=mock_repo, user_repo=AsyncMock())
    
    # Mock existing branch
    existing_branch = BranchModel(id="existing", name="Existing Branch", location="City")
    mock_repo.find_by_name.return_value = existing_branch
    
    # Test
    db = AsyncMock()
    with pytest.raises(ValidationException):
        await service.create_branch("Existing Branch", "City", None, None, None, db)


@pytest.mark.asyncio
async def test_branch_service_get_nonexistent_branch():
    """Test getting non-existent branch raises exception"""
    mock_repo = AsyncMock()
    service = BranchService(branch_repo=mock_repo, user_repo=AsyncMock())
    
    # Mock no branch found
    mock_repo.get_by_id.return_value = None
    
    # Test
    db = AsyncMock()
    with pytest.raises(NotFoundException):
        await service.get_branch("nonexistent-id", db)


@pytest.mark.asyncio
async def test_youth_service_create_youth():
    """Test creating a youth profile"""
    mock_youth_repo = AsyncMock()
    mock_branch_repo = AsyncMock()
    service = YouthService(youth_repo=mock_youth_repo, branch_repo=mock_branch_repo)
    
    # Mock branch exists
    mock_branch = BranchModel(id="branch-1", name="Branch", location="City")
    mock_branch_repo.get_by_id.return_value = mock_branch
    
    # Mock save
    from app.domain.value_objects.enums import Gender
    mock_youth = YouthModel(
        id="youth-1", fullname="New Youth", branch_id="branch-1",
        gender=Gender.MALE.value
    )
    mock_youth_repo.save.return_value = mock_youth
    
    # Test
    db = AsyncMock()
    from app.domain.value_objects.enums import Gender
    result = await service.create_youth(
        "New Youth", "branch-1", Gender.MALE, None, None, None, None, db
    )
    
    assert result.fullname == "New Youth"
    mock_branch_repo.get_by_id.assert_called_once()
    mock_youth_repo.save.assert_called_once()
