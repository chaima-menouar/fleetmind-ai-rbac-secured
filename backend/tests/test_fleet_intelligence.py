"""Tests for deterministic fleet intelligence used to ground assistants."""

from app.services.fleet_intelligence import fleet_kpis, grounding_block, ranked_risks
from app.services.store import store


def test_fleet_intelligence_prioritizes_operational_risk() -> None:
    fleet = store.vehicles()
    ranked = ranked_risks(fleet)
    assert ranked[0][0].id == "FM-4410"
    assert ranked[0][1] >= 60


def test_fleet_kpis_are_derived_from_visible_fleet() -> None:
    kpis = {item.label: item.value for item in fleet_kpis(store.vehicles())}
    assert kpis["Availability"] == "3/5"
    assert kpis["Service due <=7d"] == "2"
    assert "FM-4410" in kpis["Critical risk"]


def test_grounding_block_contains_verified_vehicle_facts() -> None:
    context = grounding_block(store.vehicles())
    assert "Verified FleetMind analytics" in context
    assert "FM-4410" in context
    assert "risk=" in context
