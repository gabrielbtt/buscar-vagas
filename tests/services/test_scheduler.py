from app.services import scheduler as scheduler_module


def test_build_scheduler_registers_interval_job():
    scheduler = scheduler_module.build_scheduler(lambda: None, interval_minutes=30)
    jobs = scheduler.get_jobs()

    assert len(jobs) == 1
    assert jobs[0].id == "job-search-cycle"


def test_build_scheduler_uses_persisted_interval_setting():
    scheduler = scheduler_module.build_scheduler(lambda: None, interval_minutes=60)
    jobs = scheduler.get_jobs()

    assert jobs[0].trigger.interval.total_seconds() == 3600


def test_run_scheduled_cycle_uses_current_settings(monkeypatch):
    scheduled_calls = []

    monkeypatch.setattr(
        scheduler_module,
        "get_settings",
        lambda refresh=False: type("Settings", (), {"search_interval_minutes": 45})(),
    )
    monkeypatch.setattr(
        scheduler_module,
        "build_runtime_collector",
        lambda settings: scheduled_calls.append(("collector", settings.search_interval_minutes)) or "collector",
    )
    monkeypatch.setattr(
        scheduler_module,
        "run_collection_cycle",
        lambda collector: scheduled_calls.append(("run", collector)) or "result",
    )

    result = scheduler_module.run_scheduled_cycle()

    assert result == "result"
    assert scheduled_calls == [("collector", 45), ("run", "collector")]


def test_sync_scheduler_interval_updates_existing_job(monkeypatch):
    scheduler = scheduler_module.build_scheduler(lambda: None, interval_minutes=30)

    monkeypatch.setattr(
        scheduler_module,
        "get_settings",
        lambda refresh=False: type("Settings", (), {"search_interval_minutes": 60})(),
    )

    scheduler_module.sync_scheduler_interval(scheduler)

    jobs = scheduler.get_jobs()
    assert jobs[0].trigger.interval.total_seconds() == 3600
