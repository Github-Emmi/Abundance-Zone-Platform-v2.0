"""
Unit Tests for Permission Checker Utility
Tests role hierarchy, branch isolation, and permission checks.

Implements: FR-AUTH-009, FR-AUTH-010, FR-SEC-002
"""

import pytest

from app.domain.value_objects.enums import Role
from app.infrastructure.security.permissions import (
    ROLE_HIERARCHY,
    can_access_branch,
    can_manage_department,
    can_modify_user_role,
    get_role_level,
    has_higher_or_equal_role,
    is_branch_coordinator,
    is_department_leader,
    is_super_admin,
    is_youth_member,
)


class TestGetRoleLevel:
    """Test role hierarchy level retrieval"""
    
    def test_super_admin_level(self):
        """SUPER_ADMIN should have level 4"""
        assert get_role_level(Role.SUPER_ADMIN) == 4
        assert get_role_level("SUPER_ADMIN") == 4
    
    def test_branch_coordinator_level(self):
        """BRANCH_COORDINATOR should have level 3"""
        assert get_role_level(Role.BRANCH_COORDINATOR) == 3
        assert get_role_level("BRANCH_COORDINATOR") == 3
    
    def test_department_leader_level(self):
        """DEPARTMENT_LEADER should have level 2"""
        assert get_role_level(Role.DEPARTMENT_LEADER) == 2
        assert get_role_level("DEPARTMENT_LEADER") == 2
    
    def test_youth_member_level(self):
        """YOUTH_MEMBER should have level 1"""
        assert get_role_level(Role.YOUTH_MEMBER) == 1
        assert get_role_level("YOUTH_MEMBER") == 1
    
    def test_invalid_role_returns_zero(self):
        """Invalid role should return 0"""
        assert get_role_level("INVALID_ROLE") == 0
        assert get_role_level("") == 0
    
    def test_role_hierarchy_ordering(self):
        """Role hierarchy should be properly ordered"""
        assert get_role_level(Role.SUPER_ADMIN) > get_role_level(Role.BRANCH_COORDINATOR)
        assert get_role_level(Role.BRANCH_COORDINATOR) > get_role_level(Role.DEPARTMENT_LEADER)
        assert get_role_level(Role.DEPARTMENT_LEADER) > get_role_level(Role.YOUTH_MEMBER)


class TestCanAccessBranch:
    """Test branch access permission checks"""
    
    def test_super_admin_can_access_any_branch(self):
        """SUPER_ADMIN can access any branch"""
        assert can_access_branch(Role.SUPER_ADMIN, None, "branch-123") is True
        assert can_access_branch(Role.SUPER_ADMIN, None, "branch-456") is True
        assert can_access_branch(Role.SUPER_ADMIN, None, None) is True
        assert can_access_branch("SUPER_ADMIN", None, "any-branch") is True
    
    def test_branch_coordinator_can_access_own_branch(self):
        """BRANCH_COORDINATOR can access own branch only"""
        assert can_access_branch(
            Role.BRANCH_COORDINATOR, "branch-123", "branch-123"
        ) is True
        assert can_access_branch(
            "BRANCH_COORDINATOR", "branch-456", "branch-456"
        ) is True
    
    def test_branch_coordinator_cannot_access_other_branch(self):
        """BRANCH_COORDINATOR cannot access other branches"""
        assert can_access_branch(
            Role.BRANCH_COORDINATOR, "branch-123", "branch-456"
        ) is False
        assert can_access_branch(
            Role.BRANCH_COORDINATOR, "branch-123", "branch-789"
        ) is False
    
    def test_branch_coordinator_cannot_access_all_branches(self):
        """BRANCH_COORDINATOR cannot access all branches (target_branch_id = None)"""
        assert can_access_branch(
            Role.BRANCH_COORDINATOR, "branch-123", None
        ) is False
    
    def test_branch_coordinator_requires_branch_assignment(self):
        """BRANCH_COORDINATOR must have branch assignment"""
        assert can_access_branch(
            Role.BRANCH_COORDINATOR, None, "branch-123"
        ) is False
    
    def test_department_leader_can_access_own_branch(self):
        """DEPARTMENT_LEADER can access own branch only"""
        assert can_access_branch(
            Role.DEPARTMENT_LEADER, "branch-123", "branch-123"
        ) is True
    
    def test_department_leader_cannot_access_other_branch(self):
        """DEPARTMENT_LEADER cannot access other branches"""
        assert can_access_branch(
            Role.DEPARTMENT_LEADER, "branch-123", "branch-456"
        ) is False
    
    def test_youth_member_can_access_own_branch(self):
        """YOUTH_MEMBER can access own branch only"""
        assert can_access_branch(
            Role.YOUTH_MEMBER, "branch-123", "branch-123"
        ) is True
    
    def test_youth_member_cannot_access_other_branch(self):
        """YOUTH_MEMBER cannot access other branches"""
        assert can_access_branch(
            Role.YOUTH_MEMBER, "branch-123", "branch-456"
        ) is False
    
    def test_invalid_role_denies_access(self):
        """Invalid role should deny access"""
        assert can_access_branch("INVALID_ROLE", "branch-123", "branch-123") is False
        assert can_access_branch("", "branch-123", "branch-123") is False


class TestCanManageDepartment:
    """Test department management permission checks"""
    
    def test_super_admin_can_manage_any_department(self):
        """SUPER_ADMIN can manage any department"""
        assert can_manage_department(Role.SUPER_ADMIN, None, "dept-123") is True
        assert can_manage_department(Role.SUPER_ADMIN, None, "dept-456") is True
        assert can_manage_department(Role.SUPER_ADMIN, None, None) is True
        assert can_manage_department("SUPER_ADMIN", None, "any-dept") is True
    
    def test_branch_coordinator_can_manage_departments_in_branch(self):
        """BRANCH_COORDINATOR can manage departments in their branch"""
        assert can_manage_department(
            Role.BRANCH_COORDINATOR,
            None,
            "dept-123",
            user_branch_id="branch-1",
            target_dept_branch_id="branch-1"
        ) is True
        
        assert can_manage_department(
            Role.BRANCH_COORDINATOR,
            None,
            "dept-456",
            user_branch_id="branch-2",
            target_dept_branch_id="branch-2"
        ) is True
    
    def test_branch_coordinator_cannot_manage_departments_in_other_branch(self):
        """BRANCH_COORDINATOR cannot manage departments in other branches"""
        assert can_manage_department(
            Role.BRANCH_COORDINATOR,
            None,
            "dept-123",
            user_branch_id="branch-1",
            target_dept_branch_id="branch-2"
        ) is False
    
    def test_branch_coordinator_allows_when_no_branch_ids_provided(self):
        """BRANCH_COORDINATOR allows when branch IDs not provided (deferred validation)"""
        assert can_manage_department(
            Role.BRANCH_COORDINATOR, None, "dept-123"
        ) is True
    
    def test_department_leader_can_manage_own_department(self):
        """DEPARTMENT_LEADER can manage own department only"""
        assert can_manage_department(
            Role.DEPARTMENT_LEADER, "dept-123", "dept-123"
        ) is True
    
    def test_department_leader_cannot_manage_other_department(self):
        """DEPARTMENT_LEADER cannot manage other departments"""
        assert can_manage_department(
            Role.DEPARTMENT_LEADER, "dept-123", "dept-456"
        ) is False
    
    def test_department_leader_cannot_manage_all_departments(self):
        """DEPARTMENT_LEADER cannot manage all departments (target_dept_id = None)"""
        assert can_manage_department(
            Role.DEPARTMENT_LEADER, "dept-123", None
        ) is False
    
    def test_department_leader_requires_department_assignment(self):
        """DEPARTMENT_LEADER must have department assignment"""
        assert can_manage_department(
            Role.DEPARTMENT_LEADER, None, "dept-123"
        ) is False
    
    def test_youth_member_cannot_manage_any_department(self):
        """YOUTH_MEMBER cannot manage any departments"""
        assert can_manage_department(Role.YOUTH_MEMBER, None, "dept-123") is False
        assert can_manage_department(Role.YOUTH_MEMBER, "dept-123", "dept-123") is False
    
    def test_invalid_role_denies_management(self):
        """Invalid role should deny management"""
        assert can_manage_department("INVALID_ROLE", "dept-123", "dept-123") is False


class TestCanModifyUserRole:
    """Test role modification permission checks"""
    
    def test_super_admin_can_assign_any_role(self):
        """SUPER_ADMIN can assign any role including SUPER_ADMIN"""
        assert can_modify_user_role(Role.SUPER_ADMIN, Role.SUPER_ADMIN) is True
        assert can_modify_user_role(Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR) is True
        assert can_modify_user_role(Role.SUPER_ADMIN, Role.DEPARTMENT_LEADER) is True
        assert can_modify_user_role(Role.SUPER_ADMIN, Role.YOUTH_MEMBER) is True
    
    def test_branch_coordinator_can_assign_lower_roles(self):
        """BRANCH_COORDINATOR can assign DEPARTMENT_LEADER and YOUTH_MEMBER"""
        assert can_modify_user_role(
            Role.BRANCH_COORDINATOR, Role.DEPARTMENT_LEADER
        ) is True
        assert can_modify_user_role(
            Role.BRANCH_COORDINATOR, Role.YOUTH_MEMBER
        ) is True
    
    def test_branch_coordinator_cannot_assign_equal_or_higher_roles(self):
        """BRANCH_COORDINATOR cannot assign BRANCH_COORDINATOR or SUPER_ADMIN"""
        assert can_modify_user_role(
            Role.BRANCH_COORDINATOR, Role.BRANCH_COORDINATOR
        ) is False
        assert can_modify_user_role(
            Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN
        ) is False
    
    def test_department_leader_cannot_assign_any_role(self):
        """DEPARTMENT_LEADER cannot assign any roles"""
        assert can_modify_user_role(Role.DEPARTMENT_LEADER, Role.SUPER_ADMIN) is False
        assert can_modify_user_role(Role.DEPARTMENT_LEADER, Role.BRANCH_COORDINATOR) is False
        assert can_modify_user_role(Role.DEPARTMENT_LEADER, Role.DEPARTMENT_LEADER) is False
        assert can_modify_user_role(Role.DEPARTMENT_LEADER, Role.YOUTH_MEMBER) is False
    
    def test_youth_member_cannot_assign_any_role(self):
        """YOUTH_MEMBER cannot assign any roles"""
        assert can_modify_user_role(Role.YOUTH_MEMBER, Role.SUPER_ADMIN) is False
        assert can_modify_user_role(Role.YOUTH_MEMBER, Role.BRANCH_COORDINATOR) is False
        assert can_modify_user_role(Role.YOUTH_MEMBER, Role.DEPARTMENT_LEADER) is False
        assert can_modify_user_role(Role.YOUTH_MEMBER, Role.YOUTH_MEMBER) is False
    
    def test_string_role_values_work(self):
        """String role values should work correctly"""
        assert can_modify_user_role("SUPER_ADMIN", "BRANCH_COORDINATOR") is True
        assert can_modify_user_role("BRANCH_COORDINATOR", "YOUTH_MEMBER") is True
        assert can_modify_user_role("YOUTH_MEMBER", "SUPER_ADMIN") is False
    
    def test_invalid_roles_deny_modification(self):
        """Invalid roles should deny modification"""
        assert can_modify_user_role("INVALID_ROLE", Role.YOUTH_MEMBER) is False
        assert can_modify_user_role(Role.SUPER_ADMIN, "INVALID_ROLE") is False
        assert can_modify_user_role("INVALID", "INVALID") is False


class TestHasHigherOrEqualRole:
    """Test role comparison checks"""
    
    def test_super_admin_higher_than_all(self):
        """SUPER_ADMIN is higher than or equal to all roles"""
        assert has_higher_or_equal_role(Role.SUPER_ADMIN, Role.SUPER_ADMIN) is True
        assert has_higher_or_equal_role(Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR) is True
        assert has_higher_or_equal_role(Role.SUPER_ADMIN, Role.DEPARTMENT_LEADER) is True
        assert has_higher_or_equal_role(Role.SUPER_ADMIN, Role.YOUTH_MEMBER) is True
    
    def test_branch_coordinator_hierarchy(self):
        """BRANCH_COORDINATOR hierarchy comparisons"""
        assert has_higher_or_equal_role(
            Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN
        ) is False
        assert has_higher_or_equal_role(
            Role.BRANCH_COORDINATOR, Role.BRANCH_COORDINATOR
        ) is True
        assert has_higher_or_equal_role(
            Role.BRANCH_COORDINATOR, Role.DEPARTMENT_LEADER
        ) is True
        assert has_higher_or_equal_role(
            Role.BRANCH_COORDINATOR, Role.YOUTH_MEMBER
        ) is True
    
    def test_department_leader_hierarchy(self):
        """DEPARTMENT_LEADER hierarchy comparisons"""
        assert has_higher_or_equal_role(
            Role.DEPARTMENT_LEADER, Role.SUPER_ADMIN
        ) is False
        assert has_higher_or_equal_role(
            Role.DEPARTMENT_LEADER, Role.BRANCH_COORDINATOR
        ) is False
        assert has_higher_or_equal_role(
            Role.DEPARTMENT_LEADER, Role.DEPARTMENT_LEADER
        ) is True
        assert has_higher_or_equal_role(
            Role.DEPARTMENT_LEADER, Role.YOUTH_MEMBER
        ) is True
    
    def test_youth_member_hierarchy(self):
        """YOUTH_MEMBER hierarchy comparisons"""
        assert has_higher_or_equal_role(Role.YOUTH_MEMBER, Role.SUPER_ADMIN) is False
        assert has_higher_or_equal_role(Role.YOUTH_MEMBER, Role.BRANCH_COORDINATOR) is False
        assert has_higher_or_equal_role(Role.YOUTH_MEMBER, Role.DEPARTMENT_LEADER) is False
        assert has_higher_or_equal_role(Role.YOUTH_MEMBER, Role.YOUTH_MEMBER) is True
    
    def test_string_role_comparisons(self):
        """String role values should work correctly"""
        assert has_higher_or_equal_role("SUPER_ADMIN", "YOUTH_MEMBER") is True
        assert has_higher_or_equal_role("YOUTH_MEMBER", "SUPER_ADMIN") is False
    
    def test_invalid_roles_return_false(self):
        """Invalid roles should return False"""
        assert has_higher_or_equal_role("INVALID", Role.YOUTH_MEMBER) is False
        assert has_higher_or_equal_role(Role.SUPER_ADMIN, "INVALID") is False


class TestRoleCheckerHelpers:
    """Test helper functions for role checking"""
    
    def test_is_super_admin(self):
        """is_super_admin should correctly identify SUPER_ADMIN role"""
        assert is_super_admin(Role.SUPER_ADMIN) is True
        assert is_super_admin("SUPER_ADMIN") is True
        assert is_super_admin(Role.BRANCH_COORDINATOR) is False
        assert is_super_admin(Role.DEPARTMENT_LEADER) is False
        assert is_super_admin(Role.YOUTH_MEMBER) is False
        assert is_super_admin("INVALID") is False
    
    def test_is_branch_coordinator(self):
        """is_branch_coordinator should correctly identify BRANCH_COORDINATOR role"""
        assert is_branch_coordinator(Role.BRANCH_COORDINATOR) is True
        assert is_branch_coordinator("BRANCH_COORDINATOR") is True
        assert is_branch_coordinator(Role.SUPER_ADMIN) is False
        assert is_branch_coordinator(Role.DEPARTMENT_LEADER) is False
        assert is_branch_coordinator(Role.YOUTH_MEMBER) is False
        assert is_branch_coordinator("INVALID") is False
    
    def test_is_department_leader(self):
        """is_department_leader should correctly identify DEPARTMENT_LEADER role"""
        assert is_department_leader(Role.DEPARTMENT_LEADER) is True
        assert is_department_leader("DEPARTMENT_LEADER") is True
        assert is_department_leader(Role.SUPER_ADMIN) is False
        assert is_department_leader(Role.BRANCH_COORDINATOR) is False
        assert is_department_leader(Role.YOUTH_MEMBER) is False
        assert is_department_leader("INVALID") is False
    
    def test_is_youth_member(self):
        """is_youth_member should correctly identify YOUTH_MEMBER role"""
        assert is_youth_member(Role.YOUTH_MEMBER) is True
        assert is_youth_member("YOUTH_MEMBER") is True
        assert is_youth_member(Role.SUPER_ADMIN) is False
        assert is_youth_member(Role.BRANCH_COORDINATOR) is False
        assert is_youth_member(Role.DEPARTMENT_LEADER) is False
        assert is_youth_member("INVALID") is False


class TestRoleHierarchyConstants:
    """Test that role hierarchy constants are correctly defined"""
    
    def test_role_hierarchy_has_all_roles(self):
        """ROLE_HIERARCHY should contain all roles"""
        assert Role.SUPER_ADMIN in ROLE_HIERARCHY
        assert Role.BRANCH_COORDINATOR in ROLE_HIERARCHY
        assert Role.DEPARTMENT_LEADER in ROLE_HIERARCHY
        assert Role.YOUTH_MEMBER in ROLE_HIERARCHY
    
    def test_role_hierarchy_values_are_correct(self):
        """ROLE_HIERARCHY should have correct numeric values"""
        assert ROLE_HIERARCHY[Role.SUPER_ADMIN] == 4
        assert ROLE_HIERARCHY[Role.BRANCH_COORDINATOR] == 3
        assert ROLE_HIERARCHY[Role.DEPARTMENT_LEADER] == 2
        assert ROLE_HIERARCHY[Role.YOUTH_MEMBER] == 1
    
    def test_role_hierarchy_is_ordered(self):
        """ROLE_HIERARCHY values should be in descending order of privilege"""
        roles = [Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR, Role.DEPARTMENT_LEADER, Role.YOUTH_MEMBER]
        levels = [ROLE_HIERARCHY[role] for role in roles]
        assert levels == sorted(levels, reverse=True)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_none_values_handled_correctly(self):
        """None values should be handled correctly"""
        # Branch access with None values
        assert can_access_branch(Role.BRANCH_COORDINATOR, None, None) is False
        assert can_access_branch(Role.SUPER_ADMIN, None, None) is True
        
        # Department management with None values
        assert can_manage_department(Role.DEPARTMENT_LEADER, None, None) is False
        assert can_manage_department(Role.SUPER_ADMIN, None, None) is True
    
    def test_empty_string_branch_ids(self):
        """Empty string branch IDs should be treated as different branches"""
        assert can_access_branch(Role.BRANCH_COORDINATOR, "", "branch-123") is False
        assert can_access_branch(Role.BRANCH_COORDINATOR, "branch-123", "") is False
    
    def test_empty_string_department_ids(self):
        """Empty string department IDs should be treated as different departments"""
        assert can_manage_department(Role.DEPARTMENT_LEADER, "", "dept-123") is False
        assert can_manage_department(Role.DEPARTMENT_LEADER, "dept-123", "") is False
    
    def test_case_sensitive_role_strings(self):
        """Role strings should be case-sensitive"""
        # These should fail because Role enum expects exact case
        assert get_role_level("super_admin") == 0
        assert get_role_level("Super_Admin") == 0
        assert get_role_level("SUPERADMIN") == 0
    
    def test_same_branch_different_departments(self):
        """Users in same branch but different departments should access branch but not manage each other's departments"""
        # Both can access the branch
        assert can_access_branch(Role.DEPARTMENT_LEADER, "branch-1", "branch-1") is True
        
        # But cannot manage each other's departments
        assert can_manage_department(
            Role.DEPARTMENT_LEADER, "dept-1", "dept-2"
        ) is False
