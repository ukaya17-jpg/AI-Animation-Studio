"""Fixed Neşeli Orman cast, location, and theme reference data.

This content was carried over verbatim from an earlier Node.js prototype; it
is small, static, and has no persistence lifecycle of its own, so it is kept
as an in-process registry rather than a database seed (mirrors how
``CameraPlanner`` holds its supported-angle vocabulary as a class constant).
"""

from __future__ import annotations

from app.models.episode_cast import EpisodeCharacter, EpisodeLocation, EpisodeTheme, VoiceProfile

_CHARACTERS: tuple[EpisodeCharacter, ...] = (
    EpisodeCharacter(
        character_id="zeytin",
        name="Zeytin",
        species="Baykuş",
        role="Bilge Öğretmen",
        core_value="Merak ve Öğrenme",
        personality=("sakin", "meraklı", "sabırlı", "bilgili"),
        visual_description=(
            "Kahverengi-turuncu tüylü, büyük yuvarlak gözlüklü genç bir baykuş. "
            "Boynunda küçük bir kitap dolu çanta taşır."
        ),
        voice=VoiceProfile(
            pitch="orta-kalın",
            pace="yavaş ve net",
            tone="sıcak, öğretmen edası",
            catchphrase="Hadi birlikte keşfedelim!",
        ),
        image_url="/static/characters/zeytin.png",
    ),
    EpisodeCharacter(
        character_id="findik",
        name="Fındık",
        species="Sincap",
        role="Enerjik Şakacı",
        core_value="Paylaşma",
        personality=("hareketli", "cömert", "komik", "sabırsız ama sevecen"),
        visual_description=(
            "Kızıl-kahve tüylü, büyük kabarık kuyruklu küçük bir sincap. "
            "Sırtında fındık topladığı minik bir çanta var."
        ),
        voice=VoiceProfile(
            pitch="tiz-ince",
            pace="hızlı, atlaya zıplaya",
            tone="neşeli, enerjik, çocuksu",
            catchphrase="Paylaşınca daha lezzetli oluyor!",
        ),
        image_url="/static/characters/findik.png",
    ),
    EpisodeCharacter(
        character_id="minik",
        name="Minik",
        species="Tavşan",
        role="Çekingen Kalp",
        core_value="Cesaret ve Arkadaşlık",
        personality=("utangaç", "nazik", "duyarlı", "gelişen özgüven"),
        visual_description=(
            "Yumuşak beyaz tüylü, uzun kulaklı küçük bir tavşan. Kulaklarından biri "
            "her zaman hafif eğik durur. Boynunda mavi bir fular vardır."
        ),
        voice=VoiceProfile(
            pitch="orta-tiz, yumuşak",
            pace="yavaş başlar, heyecanlandıkça hızlanır",
            tone="nazik, kırılgan ama sıcak",
            catchphrase="Sanırım... deneyebilirim!",
        ),
        image_url="/static/characters/minik.png",
    ),
    EpisodeCharacter(
        character_id="boncuk",
        name="Boncuk",
        species="Ayı Yavrusu",
        role="Koruyucu Büyük Kardeş",
        core_value="Yardımlaşma ve Aile",
        personality=("güçlü", "koruyucu", "sakin", "güvenilir"),
        visual_description=(
            "İri yapılı ama sevimli, koyu kahverengi tüylü bir ayı yavrusu. "
            "Patisinde ailesinden kalma küçük bir yonga (kolye) taşır."
        ),
        voice=VoiceProfile(
            pitch="kalın",
            pace="sakin, kararlı",
            tone="güven verici, babacan/ablacan sıcaklığında",
            catchphrase="Birlikte taşırsak, yük hafifler.",
        ),
        image_url="/static/characters/boncuk.png",
    ),
    EpisodeCharacter(
        character_id="papatya",
        name="Papatya",
        species="Arı",
        role="Çalışkan Takım Oyuncusu",
        core_value="Takım Çalışması ve Sayılar/Bilim",
        personality=("çalışkan", "düzenli", "meraklı", "pozitif"),
        visual_description=(
            "Sarı-siyah çizgili, parlak saydam kanatlı küçük bir arı. Küçük bir "
            "defter ve kalem taşır, her şeyi sayar/not eder."
        ),
        voice=VoiceProfile(
            pitch="parlak, orta-tiz",
            pace="canlı, ritmik",
            tone="pozitif, enerjik, düzenli",
            catchphrase="Bir, iki, üç... birlikte daha güçlüyüz!",
        ),
        image_url="/static/characters/papatya.png",
    ),
)

_LOCATIONS: tuple[EpisodeLocation, ...] = (
    EpisodeLocation(
        location_id="buyuk_mese",
        name="Büyük Meşe Ağacı",
        type="Ana Üs / Toplanma Yeri",
        description=(
            "Ormanın ortasında duran, kovuğunda Zeytin'in yaşadığı, gövdesinde "
            "herkesin toplandığı dev bir meşe ağacı."
        ),
        image_url="/static/locations/buyuk_mese.png",
    ),
    EpisodeLocation(
        location_id="gokkusagi_nehri",
        name="Gökkuşağı Nehri",
        type="Doğa / Keşif Alanı",
        description="Berrak, ışıltılı bir nehir. Doğa ve bilim temalı bölümler burada geçer.",
        image_url="/static/locations/gokkusagi_nehri.png",
    ),
    EpisodeLocation(
        location_id="paylasim_bahcesi",
        name="Paylaşım Bahçesi",
        type="Topluluk / Aile Alanı",
        description=(
            "Herkesin birlikte sebze-meyve yetiştirdiği, hasadı paylaştığı ortak bahçe."
        ),
        image_url="/static/locations/paylasim_bahcesi.png",
    ),
    EpisodeLocation(
        location_id="yildiz_tepesi",
        name="Yıldız Tepesi",
        type="Akşam / Kapanış Alanı",
        description=(
            "Ormanın en yüksek noktası, gece yıldızların net göründüğü bir tepe. "
            "Bölümler burada kapanır."
        ),
        image_url="/static/locations/yildiz_tepesi.png",
    ),
)

_THEMES: tuple[EpisodeTheme, ...] = (
    EpisodeTheme(
        theme_id="paylasma",
        label="Paylaşma",
        lead_character_id="findik",
        support_character_id="boncuk",
        location_id="paylasim_bahcesi",
        lesson=(
            "Sahip olduklarımızı paylaştığımızda, aslında kaybetmeyiz; daha çok "
            "kazanırız çünkü mutluluk çoğalır."
        ),
    ),
    EpisodeTheme(
        theme_id="arkadaslik",
        label="Arkadaşlık",
        lead_character_id="minik",
        support_character_id="findik",
        location_id="buyuk_mese",
        lesson=(
            "Gerçek bir arkadaş, sen farklı olsan bile seni olduğun gibi kabul eder "
            "ve yanında durur."
        ),
    ),
    EpisodeTheme(
        theme_id="yardimlasma",
        label="Yardımlaşma",
        lead_character_id="boncuk",
        support_character_id="papatya",
        location_id="buyuk_mese",
        lesson=(
            "Birlikte taşınan bir yük her zaman daha hafiftir; yardım istemek "
            "güçsüzlük değil, akıllılıktır."
        ),
    ),
    EpisodeTheme(
        theme_id="aile",
        label="Aile Sevgisi",
        lead_character_id="boncuk",
        support_character_id="zeytin",
        location_id="paylasim_bahcesi",
        lesson=(
            "Aile; kan bağından çok, birbirine sahip çıkan ve birbirini önemseyen "
            "herkestir."
        ),
    ),
    EpisodeTheme(
        theme_id="cesaret",
        label="Cesaret",
        lead_character_id="minik",
        support_character_id="zeytin",
        location_id="gokkusagi_nehri",
        lesson="Cesaret, korkmamak değil; korkuyla birlikte bir adım atabilmektir.",
    ),
    EpisodeTheme(
        theme_id="takim_calismasi",
        label="Takım Çalışması",
        lead_character_id="papatya",
        support_character_id="findik",
        location_id="gokkusagi_nehri",
        lesson=(
            "Herkes farklı bir şeyde iyidir; birlikte çalışınca tek başımıza "
            "yapamayacağımız şeyleri başarırız."
        ),
    ),
    EpisodeTheme(
        theme_id="sayilar",
        label="Sayılar ve Matematik",
        lead_character_id="papatya",
        support_character_id="minik",
        location_id="paylasim_bahcesi",
        lesson=(
            "Saymak her yerdedir; etrafımızdaki her şeyi sayarak matematiği "
            "eğlenceli bir oyuna çevirebiliriz."
        ),
    ),
    EpisodeTheme(
        theme_id="doga_bilim",
        label="Doğa ve Bilim",
        lead_character_id="zeytin",
        support_character_id="papatya",
        location_id="gokkusagi_nehri",
        lesson=(
            "Doğayı gözlemlemek, en büyük bilim deneyidir; her canlının doğada "
            "özel bir görevi vardır."
        ),
    ),
    EpisodeTheme(
        theme_id="duygular",
        label="Duyguları Tanımak",
        lead_character_id="minik",
        support_character_id="boncuk",
        location_id="yildiz_tepesi",
        lesson=(
            "Üzülmek, kızmak ya da korkmak normaldir; önemli olan bu duyguları "
            "anlatabilmektir."
        ),
    ),
)


class ContentBank:
    """Look up the fixed Neşeli Orman cast, locations, and themes by id."""

    def __init__(self) -> None:
        self._characters = {character.character_id: character for character in _CHARACTERS}
        self._locations = {location.location_id: location for location in _LOCATIONS}
        self._themes = {theme.theme_id: theme for theme in _THEMES}

    def get_character(self, character_id: str) -> EpisodeCharacter:
        """Return a character by id, with a clear error for an unknown reference."""
        try:
            return self._characters[character_id]
        except KeyError as error:
            raise KeyError(f"Unknown character id: {character_id}") from error

    def get_location(self, location_id: str) -> EpisodeLocation:
        """Return a location by id, with a clear error for an unknown reference."""
        try:
            return self._locations[location_id]
        except KeyError as error:
            raise KeyError(f"Unknown location id: {location_id}") from error

    def get_theme(self, theme_id: str) -> EpisodeTheme:
        """Return a theme by id, with a clear error for an unknown reference."""
        try:
            return self._themes[theme_id]
        except KeyError as error:
            raise KeyError(f"Unknown theme id: {theme_id}") from error

    def list_themes(self) -> list[EpisodeTheme]:
        """Return every supported theme."""
        return list(self._themes.values())
