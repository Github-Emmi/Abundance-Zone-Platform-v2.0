"""Repository Unit Tests"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.branch_repository import BranchRepository
from app.infrastructure.repositories.youth_repository import YouthRepository
from app.infrastructure.database.models.branch import BranchModel
from app.infrastructure.database.models.youth import YouthModel
from app.domain.value_objects.enums import MembershipStatus


@pytest.mark.asyncio
async def test_branch_repository_get_by_id():
    """Test branch repository get_by_id"""
    repo = BranchRepository()
    db = AsyncMock(spec=AsyncSession)
    
    # Mock the database result
    mock_branch = BranchModel(id="branch-1", name="Test Branch", location="Test City")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_branch
    db.execute.return_value = mock_result
    
    # Test
    result = await repo.get_by_id("branch-1", db)
    
    assert result == mock_branch
    db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_branch_repository_count_active():
    """Test counting active branches"""
    repo = BranchRepository()
    db = AsyncMock(spec=AsyncSession)
    
    # Mock count result
    mock_result = MagicMock()
    mock_result.scalar.return_value = 5
    db.execute.return_value = mock_result
    
    # Test
    count = await repo.count_active(db)
    
    assert count == 5
    db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_youth_repository_search():
    """Test youth search functionality"""
    repo = YouthRepository()
    db = AsyncMock(spec=AsyncSession)
    
    # Mock search results
    mock_youth = YouthModel(
        id="youth-1",
        fullname="Test Youth",
        email="test@youth.com",
        gender="MALE",
        branch_id="branch-1",
        membership_status=MembershipStatus.ACTIVE.value
    )
    
    mock_count = MagicMock()
    mock_count.scalar.return_value = 1
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_youth]
    
    db.execute.side_effect = [mock_count, mock_result]
    
    # Test
    results, total = await repo.search("Test", None, 0, 10, db)
    
    assert total == 1
    assert len(results) == 1
    assert results[0].fullname == "Test Youth"
