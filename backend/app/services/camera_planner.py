"""Camera planning for readable, varied scene compositions."""

from __future__ import annotations

from app.models.scene import CameraSetting


class CameraPlanner:
    """Choose from the studio's supported camera vocabulary."""

    SUPPORTED_ANGLES = (
        "Wide",
        "Medium",
        "Close-up",
        "Extreme Close-up",
        "Top View",
        "Low Angle",
        "High Angle",
        "Tracking",
        "Pan",
        "Zoom",
        "Orbit",
    )

    def plan(self, scene_number: int, text: str = "") -> CameraSetting:
        """Return a deterministic shot that avoids consecutive uniform framing."""
        angle = self.SUPPORTED_ANGLES[(scene_number - 1) % len(self.SUPPORTED_ANGLES)]
        movement = (
            "Static"
            if angle in {"Wide", "Medium", "Close-up", "Top View", "Low Angle", "High Angle"}
            else angle
        )
        lens = "24mm" if angle == "Wide" else "85mm" if "Close" in angle else "50mm"
        return CameraSetting(angle=angle, movement=movement, lens=lens)
