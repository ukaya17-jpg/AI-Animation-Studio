from app.services.storyboard_builder import StoryboardBuilder
from app.services.storyboard_exporter import ExportFormat, StoryboardExporter


def test_builder_preserves_requested_duration_and_creates_thirty_minute_scene_range() -> None:
    storyboard = StoryboardBuilder().build(
        "A visual lesson explains a concept with clear examples. " * 100,
        total_duration=30 * 60,
        title="Duration test",
    )

    assert 100 <= len(storyboard.scenes) <= 150
    assert len(storyboard.scenes) == 120
    assert storyboard.total_duration == 1800
    assert sum(scene.duration for scene in storyboard.scenes) == 1800
    assert storyboard.scenes[0].start_time == 0
    assert storyboard.scenes[-1].end_time == 1800


def test_builder_creates_a_continuous_timeline_and_scene_fields() -> None:
    storyboard = StoryboardBuilder().build("The sun rises. The class begins.", total_duration=20)

    assert storyboard.scenes[0].scene_id == "scene-0001"
    assert all(
        scene.end_time == next_scene.start_time
        for scene, next_scene in zip(storyboard.scenes, storyboard.scenes[1:], strict=False)
    )
    assert all(scene.environment.location for scene in storyboard.scenes)
    assert all(scene.camera.angle for scene in storyboard.scenes)
    assert all(scene.narration or scene.dialogues for scene in storyboard.scenes)


def test_exporter_supports_json_markdown_and_yaml() -> None:
    storyboard = StoryboardBuilder().build(
        "A calm opening scene.", total_duration=5, title="Export test"
    )
    exporter = StoryboardExporter()

    assert '"title": "Export test"' in exporter.export(storyboard, ExportFormat.JSON)
    assert "# Export test" in exporter.export(storyboard, "markdown")
    assert 'title: "Export test"' in exporter.export(storyboard, "yaml")
