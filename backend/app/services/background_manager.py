"""Create coherent environments for storyboard scenes."""

from __future__ import annotations

from app.models.scene import EnvironmentSetting


class BackgroundManager:
    """Derive a compact environment specification from scene text."""

    _PALETTES = (
        ("#1D3557", "#457B9D", "#A8DADC"),
        ("#264653", "#2A9D8F", "#E9C46A"),
        ("#3D405B", "#81B29A", "#F4F1DE"),
    )

    def create_environment(self, text: str, scene_number: int = 1) -> EnvironmentSetting:
        """Produce deterministic lighting, weather, palette, and perspective."""
        lowered = text.casefold()
        location = self._location_for(lowered)
        lighting = "warm golden-hour light" if "night" not in lowered else "cinematic moonlight"
        weather = "rain" if "rain" in lowered else "clear"
        return EnvironmentSetting(
            location=location,
            lighting=lighting,
            weather=weather,
            color_palette=self._PALETTES[(scene_number - 1) % len(self._PALETTES)],
            perspective="layered cinematic depth",
        )

    @staticmethod
    def _location_for(text: str) -> str:
        for word, location in (
            ("classroom", "classroom"),
            ("forest", "forest clearing"),
            ("office", "modern office"),
            ("home", "cozy home interior"),
            ("street", "city street"),
        ):
            if word in text:
                return location
        return "stylized narrative setting"
