"""shot_bible_ref_stripper 单元测试。"""


def test_strip_prop_ids_from_shot() -> None:
    """应移除指定 prop_ids。"""
    from app.models.postgres.shot_model import ShotModel
    from app.video.shot_bible_ref_stripper import apply_bible_ref_strip

    shot = ShotModel(
        shot_id="s1",
        project_id="demo",
        shot_no="1",
        duration_sec=3,
        prop_ids=["brand", "product", "sword"],
    )
    changed = apply_bible_ref_strip(shot, set(), set(), {"brand", "product"})
    assert changed is True
    assert shot.prop_ids == ["sword"]


def test_strip_scene_id_clears_field() -> None:
    """匹配 scene_id 应清空字符串。"""
    from app.models.postgres.shot_model import ShotModel
    from app.video.shot_bible_ref_stripper import apply_bible_ref_strip

    shot = ShotModel(
        shot_id="s1",
        project_id="demo",
        shot_no="1",
        duration_sec=3,
        scene_id="scene_a",
    )
    changed = apply_bible_ref_strip(shot, set(), {"scene_a"}, set())
    assert changed is True
    assert shot.scene_id == ""


def test_strip_no_op_when_ids_absent() -> None:
    """无匹配 ID 时不应改动。"""
    from app.models.postgres.shot_model import ShotModel
    from app.video.shot_bible_ref_stripper import apply_bible_ref_strip

    shot = ShotModel(
        shot_id="s1",
        project_id="demo",
        shot_no="1",
        duration_sec=3,
        character_ids=["char_a"],
    )
    changed = apply_bible_ref_strip(shot, {"char_missing"}, set(), set())
    assert changed is False
    assert shot.character_ids == ["char_a"]
