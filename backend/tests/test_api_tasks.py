import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ONLINE"

@pytest.mark.asyncio
async def test_full_task_crud_and_plan_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create Task (POST /api/v1/tasks)
        payload = {
            "title": "Audit Task - Prepare Semester Report",
            "description": "Comprehensive integration test task",
            "category": "COLLEGE",
            "priority": "MUST_DO",
            "estimated_duration": 45,
            "source": "MANUAL_INPUT",
            "consequence": "Must be completed prior to evaluation",
            "dependencies": []
        }
        create_res = await ac.post("/api/v1/tasks", json=payload)
        assert create_res.status_code == 201, f"Expected 201, got {create_res.status_code}: {create_res.text}"
        data = create_res.json()
        assert data["title"] == payload["title"]
        assert "id" in data
        task_id = data["id"]

        # 2. Get Task List (GET /api/v1/tasks)
        list_res = await ac.get("/api/v1/tasks")
        assert list_res.status_code == 200
        tasks = list_res.json()
        assert any(t["id"] == task_id for t in tasks)

        # 3. Get Task By ID (GET /api/v1/tasks/{id})
        get_res = await ac.get(f"/api/v1/tasks/{task_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == task_id

        # 4. Patch Task (PATCH /api/v1/tasks/{id})
        patch_res = await ac.patch(f"/api/v1/tasks/{task_id}", json={"priority": "SHOULD_DO", "estimated_duration": 50})
        assert patch_res.status_code == 200
        assert patch_res.json()["priority"] == "SHOULD_DO"
        assert patch_res.json()["estimated_duration"] == 50

        # 5. Complete Task (POST /api/v1/tasks/{id}/complete)
        comp_res = await ac.post(f"/api/v1/tasks/{task_id}/complete", json={"actual_duration_minutes": 45})
        assert comp_res.status_code == 200
        assert comp_res.json()["status"] == "COMPLETED"

        # 6. Delete Task (DELETE /api/v1/tasks/{id})
        del_res = await ac.delete(f"/api/v1/tasks/{task_id}")
        assert del_res.status_code == 200

        # 7. Check Today Plan (GET /api/v1/plans/today)
        plan_res = await ac.get("/api/v1/plans/today")
        assert plan_res.status_code == 200
        assert "items" in plan_res.json()

        # 8. Trigger Replan (POST /api/v1/plans/replan)
        replan_res = await ac.post("/api/v1/plans/replan", json={"reason": "Audit Test Replan"})
        assert replan_res.status_code == 200
        assert replan_res.json()["is_active"] is True

@pytest.mark.asyncio
async def test_timezone_aware_deadline_handling():
    """Verifies that mixing offset-aware and offset-naive ISO deadlines does not crash the planner or tasks API."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create task with timezone-aware deadline (+00:00)
        res1 = await ac.post("/api/v1/tasks", json={
            "title": "Timezone Aware Task 1",
            "deadline": "2026-09-15T18:00:00+00:00",
            "priority": "MUST_DO"
        })
        assert res1.status_code == 201
        t1_id = res1.json()["id"]

        # Create task with offset-naive deadline string
        res2 = await ac.post("/api/v1/tasks", json={
            "title": "Timezone Aware Task 2",
            "deadline": "2026-09-16T10:00:00",
            "priority": "SHOULD_DO"
        })
        assert res2.status_code == 201
        t2_id = res2.json()["id"]

        # Update task 1 deadline
        patch_res = await ac.patch(f"/api/v1/tasks/{t1_id}", json={
            "deadline": "2026-09-14T12:00:00Z"
        })
        assert patch_res.status_code == 200

        # Trigger plan to verify sorting across tasks with diverse deadline formats
        plan_res = await ac.get("/api/v1/plans/today")
        assert plan_res.status_code == 200

        # Cleanup
        await ac.delete(f"/api/v1/tasks/{t1_id}")
        await ac.delete(f"/api/v1/tasks/{t2_id}")

