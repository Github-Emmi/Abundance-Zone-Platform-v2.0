"""Finance Reports API Router"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from celery.result import AsyncResult

from app.api.deps import CurrentUser, get_current_user, require_role
from app.api.schemas.responses import ApiResponse
from app.domain.value_objects.enums import Role
from app.tasks.reports import generate_monthly_financial_report
from app.tasks.celery_app import celery_app
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/finance", tags=["Finance Reports"])


# ═══════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════


class MonthlyReportRequest(BaseModel):
    """Request schema for monthly financial report."""

    month: str | None = Field(
        None, description="Month in YYYY-MM format (defaults to current month)"
    )


class ReportStatusResponse(BaseModel):
    """Response schema for report status check."""

    task_id: str
    state: str
    status: str
    result: dict | None = None
    error: str | None = None


class MonthlyReportResponse(BaseModel):
    """Response schema for monthly report generation."""

    task_id: str | None
    status: str
    message: str
    month: str | None
    timestamp: str


# ═══════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "/reports/monthly",
    response_model=ApiResponse[MonthlyReportResponse],
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
async def generate_monthly_report(
    data: MonthlyReportRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Generate monthly financial report (pledges and payments).

    **Protected Endpoint** (SUPER_ADMIN only)

    **Business Rules:**
    - Only SUPER_ADMIN can access financial reports (sensitive data)
    - Generates comprehensive monthly financial summary
    - Includes pledge commitments, payments received, outstanding balances
    - Runs asynchronously via Celery (1-2 minutes typical)

    **Request Body:**
    - month: Month in YYYY-MM format (optional, defaults to current month)

    **Returns:**
    - task_id: Celery task ID for tracking report generation
    - status: "queued" or "error"
    - message: Status message
    - month: Month being reported on
    - timestamp: When report generation was queued

    **Report Contents:**
    - Total pledges made during the month
    - Total payments received
    - Outstanding pledge balances
    - Payment rate (% of pledges fulfilled)
    - Breakdown by payment method (if applicable)
    - Top contributors/pledgers

    **Note:**
    This endpoint requires pledge and payment models to be fully implemented.
    Currently returns placeholder data structure for development/testing.

    **Use Cases:**
    - Monthly board reports
    - Financial audits and compliance
    - Donor recognition programs
    - Budget forecasting
    - Grant reporting requirements

    **Performance:**
    - Generation typically takes 1-2 minutes
    - Check status via GET /finance/reports/{task_id}/status
    - Download CSV via GET /finance/reports/{task_id}/download

    **Security:**
    - Access restricted to SUPER_ADMIN only
    - Financial data is highly sensitive
    - Audit log maintained for all access

    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "finance-report-abc-123",
            "status": "queued",
            "message": "Monthly financial report generation started",
            "month": "2024-01",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    }
    ```
    """
    month = data.month
    task_id = None

    try:
        task = generate_monthly_financial_report.delay(month=month)
        task_id = task.id
        logger.info(
            f"Dispatched monthly financial report task {task_id} for month {month or 'current'}"
        )
        status_str = "queued"
        message = f"Monthly financial report generation started for {month or 'current month'}"
    except Exception as e:
        logger.error(f"Failed to dispatch monthly financial report task: {e}")
        status_str = "error"
        message = "Failed to queue monthly financial report generation"

    return ApiResponse(
        data=MonthlyReportResponse(
            task_id=task_id,
            status=status_str,
            message=message,
            month=month,
            timestamp=datetime.utcnow().isoformat(),
        )
    )


@router.get(
    "/reports/{task_id}/status",
    response_model=ApiResponse[ReportStatusResponse],
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
async def get_report_status(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Check status of financial report generation task.

    **Protected Endpoint** (SUPER_ADMIN only)

    **Path Parameters:**
    - task_id: Celery task ID returned from report generation endpoint

    **Returns:**
    - task_id: The task ID being checked
    - state: Celery task state (PENDING/STARTED/SUCCESS/FAILURE)
    - status: Human-readable status (processing/completed/failed)
    - result: Report data if complete (null if still processing)
    - error: Error message if failed (null otherwise)

    **Task States:**
    - **PENDING**: Task queued but not started yet
    - **STARTED**: Task is currently processing
    - **SUCCESS**: Task completed successfully, result available
    - **FAILURE**: Task failed, error details provided
    - **RETRY**: Task failed and is being retried

    **Use Cases:**
    - Poll for report completion
    - Display progress to user
    - Handle errors gracefully
    - Determine when to download result

    **Example Response (Processing):**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "abc-123",
            "state": "STARTED",
            "status": "processing",
            "result": null,
            "error": null
        }
    }
    ```

    **Example Response (Completed):**
    ```json
    {
        "success": true,
        "data": {
            "task_id": "abc-123",
            "state": "SUCCESS",
            "status": "completed",
            "result": {
                "month": "2024-01",
                "total_pledges": 15000,
                "total_paid": 12000,
                "payment_rate": 80.0
            },
            "error": null
        }
    }
    ```
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        # Map Celery states to human-readable status
        state = task_result.state
        if state == "PENDING":
            status_str = "queued"
        elif state == "STARTED":
            status_str = "processing"
        elif state == "SUCCESS":
            status_str = "completed"
        elif state == "FAILURE":
            status_str = "failed"
        else:
            status_str = state.lower()

        # Get result or error
        result_data = None
        error_msg = None

        if state == "SUCCESS":
            result_data = task_result.result
        elif state == "FAILURE":
            error_msg = str(task_result.info)

        return ApiResponse(
            data=ReportStatusResponse(
                task_id=task_id,
                state=state,
                status=status_str,
                result=result_data,
                error=error_msg,
            )
        )

    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}",
        )


@router.get(
    "/reports/{task_id}/download",
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
async def download_report(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Download financial report CSV.

    **Protected Endpoint** (SUPER_ADMIN only)

    **Path Parameters:**
    - task_id: Celery task ID returned from report generation endpoint

    **Returns:**
    - CSV file download if report is ready
    - 202 Accepted if report still processing
    - 400 Bad Request if report generation failed
    - 404 Not Found if task_id invalid

    **Response Headers:**
    - Content-Type: text/csv
    - Content-Disposition: attachment; filename=financial_report_{month}.csv

    **CSV Format:**
    ```
    Month,Total Pledges,Total Paid,Total Pending,Payment Rate
    January 2024,15000,12000,3000,80.0%

    [Detailed breakdown follows...]
    ```

    **Use Cases:**
    - Export for spreadsheet analysis
    - Archive for record-keeping
    - Share with board members
    - Import into accounting software

    **Performance:**
    - Instant download if report cached
    - Retry if 202 received (not ready yet)
    - Implement client-side retry with exponential backoff

    **Security:**
    - Access logged for audit trail
    - Download counts tracked
    - Financial data encrypted in transit

    **Example Usage:**
    ```javascript
    // JavaScript client polling pattern
    async function downloadReport(taskId) {
        const response = await fetch(`/api/v1/finance/reports/${taskId}/download`);

        if (response.status === 202) {
            // Still processing, wait and retry
            await sleep(2000);
            return downloadReport(taskId);
        }

        if (response.ok) {
            // Download ready
            const blob = await response.blob();
            saveAs(blob, 'financial_report.csv');
        }
    }
    ```
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        if task_result.state == "PENDING":
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Report generation in progress, please try again shortly",
            )

        if task_result.state == "STARTED":
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Report is being generated, please wait",
            )

        if task_result.state == "FAILURE":
            error_msg = str(task_result.info)
            logger.error(f"Report generation failed for task {task_id}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report generation failed: {error_msg}",
            )

        if task_result.state == "SUCCESS":
            result = task_result.result

            # Check if result has CSV content
            csv_content = result.get("csv_content", "")

            if not csv_content:
                # No CSV content, return JSON result instead
                logger.warning(f"Task {task_id} completed but no CSV content available")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Report data not available. Note: Financial reporting requires pledge/payment models.",
                )

            # Generate filename from month if available
            month = result.get("month", "unknown")
            filename = f"financial_report_{month}.csv"

            logger.info(f"Serving financial report download for task {task_id}")

            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        # Unknown state
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected task state: {task_result.state}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download report for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}",
        )
