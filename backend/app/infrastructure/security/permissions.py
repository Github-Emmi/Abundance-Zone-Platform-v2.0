"""
Permission Checker Utility
Implements role-based access control (RBAC) with 4-tier role hierarchy.

Role Hierarchy (Level 4 → Level 1):
- SUPER_ADMIN (Level 4): Full system access, all branches
- BRANCH_COORDINATOR (Level 3): Own branch management only
- DEPARTMENT_LEADER (Level 2): Own department only
- YOUTH_MEMBER (Level 1): Self-access only

Implements: FR-AUTH-009, FR-AUTH-010, FR-SEC-002
"""

from app.domain.value_objects.enums import Role


# Role hierarchy levels (higher = more privileges)
ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 4,
    Role.BRANCH_COORDINATOR: 3,
    Role.DEPARTMENT_LEADER: 2,
    Role.YOUTH_MEMBER: 1,
}


def get_role_level(role: str | Role) -> int:
    """
    Get the hierarchy level for a given role.
    
    Args:
        role: Role enum value or string representation
        
    Returns:
        int: Hierarchy level (1-4), or 0 if role is invalid
        
    Examples:
        >>> get_role_level(Role.SUPER_ADMIN)
        4
        >>> get_role_level("BRANCH_COORDINATOR")
        3
        >>> get_role_level("INVALID_ROLE")
        0
    """
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return 0
    return ROLE_HIERARCHY.get(role, 0)


def can_access_branch(
    user_role: str | Role,
    user_branch_id: str | None,
    target_branch_id: str | None
) -> bool:
    """
    Check if a user can access resources from a specific branch.
    
    Business Rules:
    - SUPER_ADMIN: Can access all branches (target_branch_id can be None or any value)
    - BRANCH_COORDINATOR: Can only access own branch (user_branch_id == target_branch_id)
    - DEPARTMENT_LEADER: Can only access own branch (user_branch_id == target_branch_id)
    - YOUTH_MEMBER: Can only access own branch (user_branch_id == target_branch_id)
    
    Args:
        user_role: Role of the user making the request
        user_branch_id: Branch ID the user belongs to (None for SUPER_ADMIN)
        target_branch_id: Branch ID being accessed (None means all branches)
        
    Returns:
        bool: True if access is allowed, False otherwise
        
    Examples:
        >>> # SUPER_ADMIN can access any branch
        >>> can_access_branch(Role.SUPER_ADMIN, None, "branch-123")
        True
        
        >>> # BRANCH_COORDINATOR can access own branch
        >>> can_access_branch(Role.BRANCH_COORDINATOR, "branch-123", "branch-123")
        True
        
        >>> # BRANCH_COORDINATOR cannot access other branches
        >>> can_access_branch(Role.BRANCH_COORDINATOR, "branch-123", "branch-456")
        False
        
        >>> # YOUTH_MEMBER can access own branch
        >>> can_access_branch(Role.YOUTH_MEMBER, "branch-123", "branch-123")
        True
    """
    role_level = get_role_level(user_role)
    
    # Invalid role
    if role_level == 0:
        return False
    
    # SUPER_ADMIN can access all branches
    if role_level == ROLE_HIERARCHY[Role.SUPER_ADMIN]:
        return True
    
    # For all other roles, can only access own branch
    # If target_branch_id is None, it means requesting all branches (not allowed)
    if target_branch_id is None:
        return False
    
    # Must have a branch assignment
    if user_branch_id is None:
        return False
    
    # Can only access own branch
    return user_branch_id == target_branch_id


def can_manage_department(
    user_role: str | Role,
    user_department_id: str | None,
    target_dept_id: str | None,
    user_branch_id: str | None = None,
    target_dept_branch_id: str | None = None
) -> bool:
    """
    Check if a user can manage resources in a specific department.
    
    Business Rules:
    - SUPER_ADMIN: Can manage all departments across all branches
    - BRANCH_COORDINATOR: Can manage all departments in their branch
    - DEPARTMENT_LEADER: Can only manage own department
    - YOUTH_MEMBER: Cannot manage any departments
    
    Args:
        user_role: Role of the user making the request
        user_department_id: Department ID the user belongs to (None if no department)
        target_dept_id: Department ID being managed (None means all departments)
        user_branch_id: Branch ID the user belongs to (for BRANCH_COORDINATOR validation)
        target_dept_branch_id: Branch ID of the target department (for BRANCH_COORDINATOR validation)
        
    Returns:
        bool: True if management is allowed, False otherwise
        
    Examples:
        >>> # SUPER_ADMIN can manage any department
        >>> can_manage_department(Role.SUPER_ADMIN, None, "dept-123")
        True
        
        >>> # BRANCH_COORDINATOR can manage departments in their branch
        >>> can_manage_department(
        ...     Role.BRANCH_COORDINATOR, None, "dept-123",
        ...     user_branch_id="branch-1", target_dept_branch_id="branch-1"
        ... )
        True
        
        >>> # DEPARTMENT_LEADER can only manage own department
        >>> can_manage_department(Role.DEPARTMENT_LEADER, "dept-123", "dept-123")
        True
        
        >>> # DEPARTMENT_LEADER cannot manage other departments
        >>> can_manage_department(Role.DEPARTMENT_LEADER, "dept-123", "dept-456")
        False
        
        >>> # YOUTH_MEMBER cannot manage departments
        >>> can_manage_department(Role.YOUTH_MEMBER, None, "dept-123")
        False
    """
    role_level = get_role_level(user_role)
    
    # Invalid role
    if role_level == 0:
        return False
    
    # SUPER_ADMIN can manage all departments
    if role_level == ROLE_HIERARCHY[Role.SUPER_ADMIN]:
        return True
    
    # BRANCH_COORDINATOR can manage all departments in their branch
    if role_level == ROLE_HIERARCHY[Role.BRANCH_COORDINATOR]:
        # If no branch IDs provided, allow (will be validated elsewhere)
        if user_branch_id is None or target_dept_branch_id is None:
            return True
        # Must be same branch
        return user_branch_id == target_dept_branch_id
    
    # DEPARTMENT_LEADER can only manage own department
    if role_level == ROLE_HIERARCHY[Role.DEPARTMENT_LEADER]:
        # Must have department assignment
        if user_department_id is None:
            return False
        # If target is None, it means all departments (not allowed)
        if target_dept_id is None:
            return False
        # Can only manage own department
        return user_department_id == target_dept_id
    
    # YOUTH_MEMBER cannot manage departments
    return False


def can_modify_user_role(
    actor_role: str | Role,
    target_role: str | Role
) -> bool:
    """
    Check if a user can modify/assign a specific role to another user.
    
    Business Rules:
    - SUPER_ADMIN: Can assign any role (including SUPER_ADMIN, BRANCH_COORDINATOR)
    - BRANCH_COORDINATOR: Can only assign DEPARTMENT_LEADER or YOUTH_MEMBER
    - DEPARTMENT_LEADER: Cannot assign any roles
    - YOUTH_MEMBER: Cannot assign any roles
    
    Role Assignment Matrix:
    Actor Role          | Can Assign Roles
    --------------------|----------------------------------------
    SUPER_ADMIN         | SUPER_ADMIN, BRANCH_COORDINATOR, DEPARTMENT_LEADER, YOUTH_MEMBER
    BRANCH_COORDINATOR  | DEPARTMENT_LEADER, YOUTH_MEMBER
    DEPARTMENT_LEADER   | None
    YOUTH_MEMBER        | None
    
    Args:
        actor_role: Role of the user attempting to modify the role
        target_role: Role being assigned to the target user
        
    Returns:
        bool: True if role assignment is allowed, False otherwise
        
    Examples:
        >>> # SUPER_ADMIN can assign any role
        >>> can_modify_user_role(Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR)
        True
        >>> can_modify_user_role(Role.SUPER_ADMIN, Role.SUPER_ADMIN)
        True
        
        >>> # BRANCH_COORDINATOR can assign lower roles only
        >>> can_modify_user_role(Role.BRANCH_COORDINATOR, Role.DEPARTMENT_LEADER)
        True
        >>> can_modify_user_role(Role.BRANCH_COORDINATOR, Role.YOUTH_MEMBER)
        True
        
        >>> # BRANCH_COORDINATOR cannot assign higher or equal roles
        >>> can_modify_user_role(Role.BRANCH_COORDINATOR, Role.BRANCH_COORDINATOR)
        False
        >>> can_modify_user_role(Role.BRANCH_COORDINATOR, Role.SUPER_ADMIN)
        False
        
        >>> # DEPARTMENT_LEADER cannot assign any roles
        >>> can_modify_user_role(Role.DEPARTMENT_LEADER, Role.YOUTH_MEMBER)
        False
        
        >>> # YOUTH_MEMBER cannot assign any roles
        >>> can_modify_user_role(Role.YOUTH_MEMBER, Role.YOUTH_MEMBER)
        False
    """
    actor_level = get_role_level(actor_role)
    target_level = get_role_level(target_role)
    
    # Invalid roles
    if actor_level == 0 or target_level == 0:
        return False
    
    # SUPER_ADMIN can assign any role (including SUPER_ADMIN)
    if actor_level == ROLE_HIERARCHY[Role.SUPER_ADMIN]:
        return True
    
    # BRANCH_COORDINATOR can only assign roles lower than their own
    # (DEPARTMENT_LEADER and YOUTH_MEMBER)
    if actor_level == ROLE_HIERARCHY[Role.BRANCH_COORDINATOR]:
        return target_level < actor_level
    
    # DEPARTMENT_LEADER and YOUTH_MEMBER cannot assign any roles
    return False


def has_higher_or_equal_role(
    user_role: str | Role,
    comparison_role: str | Role
) -> bool:
    """
    Check if a user's role is higher than or equal to another role in the hierarchy.
    
    Args:
        user_role: Role of the user
        comparison_role: Role to compare against
        
    Returns:
        bool: True if user_role >= comparison_role in hierarchy, False otherwise
        
    Examples:
        >>> has_higher_or_equal_role(Role.SUPER_ADMIN, Role.BRANCH_COORDINATOR)
        True
        >>> has_higher_or_equal_role(Role.BRANCH_COORDINATOR, Role.BRANCH_COORDINATOR)
        True
        >>> has_higher_or_equal_role(Role.YOUTH_MEMBER, Role.DEPARTMENT_LEADER)
        False
    """
    user_level = get_role_level(user_role)
    comparison_level = get_role_level(comparison_role)
    
    # Invalid roles
    if user_level == 0 or comparison_level == 0:
        return False
    
    return user_level >= comparison_level


def is_super_admin(user_role: str | Role) -> bool:
    """
    Check if a user has SUPER_ADMIN role.
    
    Args:
        user_role: Role of the user
        
    Returns:
        bool: True if user is SUPER_ADMIN, False otherwise
        
    Examples:
        >>> is_super_admin(Role.SUPER_ADMIN)
        True
        >>> is_super_admin("SUPER_ADMIN")
        True
        >>> is_super_admin(Role.BRANCH_COORDINATOR)
        False
    """
    return get_role_level(user_role) == ROLE_HIERARCHY[Role.SUPER_ADMIN]


def is_branch_coordinator(user_role: str | Role) -> bool:
    """
    Check if a user has BRANCH_COORDINATOR role.
    
    Args:
        user_role: Role of the user
        
    Returns:
        bool: True if user is BRANCH_COORDINATOR, False otherwise
        
    Examples:
        >>> is_branch_coordinator(Role.BRANCH_COORDINATOR)
        True
        >>> is_branch_coordinator("BRANCH_COORDINATOR")
        True
        >>> is_branch_coordinator(Role.SUPER_ADMIN)
        False
    """
    return get_role_level(user_role) == ROLE_HIERARCHY[Role.BRANCH_COORDINATOR]


def is_department_leader(user_role: str | Role) -> bool:
    """
    Check if a user has DEPARTMENT_LEADER role.
    
    Args:
        user_role: Role of the user
        
    Returns:
        bool: True if user is DEPARTMENT_LEADER, False otherwise
        
    Examples:
        >>> is_department_leader(Role.DEPARTMENT_LEADER)
        True
        >>> is_department_leader("DEPARTMENT_LEADER")
        True
        >>> is_department_leader(Role.YOUTH_MEMBER)
        False
    """
    return get_role_level(user_role) == ROLE_HIERARCHY[Role.DEPARTMENT_LEADER]


def is_youth_member(user_role: str | Role) -> bool:
    """
    Check if a user has YOUTH_MEMBER role.
    
    Args:
        user_role: Role of the user
        
    Returns:
        bool: True if user is YOUTH_MEMBER, False otherwise
        
    Examples:
        >>> is_youth_member(Role.YOUTH_MEMBER)
        True
        >>> is_youth_member("YOUTH_MEMBER")
        True
        >>> is_youth_member(Role.DEPARTMENT_LEADER)
        False
    """
    return get_role_level(user_role) == ROLE_HIERARCHY[Role.YOUTH_MEMBER]
