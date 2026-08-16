from app.services.character_manager import CharacterManager
from app.services.storyboard_builder import StoryboardBuilder


def test_character_manager_keeps_a_stable_identity_for_same_name() -> None:
    manager = CharacterManager()
    first = manager.create_character("Ada", hair="curly black hair", colors=("#101010", "#ffcc00"))
    second = manager.create_character(" ada ")
    reference = manager.get_or_create_reference("ADA", expression="happy")

    assert first == second
    assert reference.character_id == first.character_id
    assert reference.expression == "happy"
    assert len(manager.list_characters()) == 1


def test_dialogue_character_is_reused_between_scenes() -> None:
    storyboard = StoryboardBuilder().build(
        "Ada: Welcome to class. Ada: Let us begin.", total_duration=10
    )
    ids = [dialogue.character_id for scene in storyboard.scenes for dialogue in scene.dialogues]

    assert ids
    assert len(set(ids)) == 1
