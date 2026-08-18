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
        voice_sample_url="/static/characters/voices/zeytin.mp3",
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
        voice_sample_url="/static/characters/voices/findik.mp3",
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
        voice_sample_url="/static/characters/voices/minik.mp3",
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
        voice_sample_url="/static/characters/voices/boncuk.mp3",
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
        voice_sample_url="/static/characters/voices/papatya.mp3",
    ),
    EpisodeCharacter(
        character_id="kurnaz",
        name="Kurnaz",
        species="Tilki",
        role="Zeki Problem Çözücü",
        core_value="Yaratıcı Düşünme",
        personality=("zeki", "kurnaz ama iyi kalpli", "kendinden emin", "meraklı"),
        visual_description=(
            "Turuncu-kızıl tüylü, beyaz göğüs lekeli, kabarık kuyruklu bir tilki. "
            "Boynunda mavi bir fular, elinde küçük bir büyüteç taşır."
        ),
        voice=VoiceProfile(
            pitch="orta-kalın, esprili",
            pace="hızlı ve zekice",
            tone="kendinden emin, esprili",
            catchphrase="Bir problem mi var? Hemen bir çözüm bulabilirim!",
        ),
        image_url="/static/characters/kurnaz.png",
        voice_sample_url="/static/characters/voices/kurnaz.mp3",
    ),
    EpisodeCharacter(
        character_id="diken",
        name="Diken",
        species="Kirpi",
        role="Çekingen ama Sevimli",
        core_value="Kendini Kabul Etme",
        personality=("utangaç", "duyarlı", "içten", "kendini geliştiren"),
        visual_description=(
            "Yuvarlak, dikenli ama sevimli görünen küçük bir kirpi. Boynunda "
            "turuncu-sarı çizgili bir atkı vardır."
        ),
        voice=VoiceProfile(
            pitch="yumuşak, orta-tiz",
            pace="yavaş, tereddütlü",
            tone="nazik, biraz çekingen ama sıcak",
            catchphrase="Ben... çok da farklı değilim aslında.",
        ),
        image_url="/static/characters/diken.png",
        voice_sample_url="/static/characters/voices/diken.mp3",
    ),
    EpisodeCharacter(
        character_id="isik",
        name="Işık",
        species="Ateşböceği",
        role="Umut Veren Rehber",
        core_value="Umut",
        personality=("umutlu", "sakin", "yol gösterici", "nazik"),
        visual_description=(
            "Küçük, yuvarlak, saydam kanatlı bir ateşböceği. Kuyruğunda sıcak "
            "sarı-altın bir parıltı vardır."
        ),
        voice=VoiceProfile(
            pitch="yumuşak, orta",
            pace="sakin, huzurlu",
            tone="umut verici, rahatlatıcı",
            catchphrase="Karanlık bazen korkutucu görünür ama merak etme, ben yolunu aydınlatırım.",
        ),
        image_url="/static/characters/isik.png",
        voice_sample_url="/static/characters/voices/isik.mp3",
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
        ambient_video_url="/static/locations/videos/buyuk_mese.mp4",
    ),
    EpisodeLocation(
        location_id="gokkusagi_nehri",
        name="Gökkuşağı Nehri",
        type="Doğa / Keşif Alanı",
        description="Berrak, ışıltılı bir nehir. Doğa ve bilim temalı bölümler burada geçer.",
        image_url="/static/locations/gokkusagi_nehri.png",
        ambient_video_url="/static/locations/videos/gokkusagi_nehri.mp4",
    ),
    EpisodeLocation(
        location_id="paylasim_bahcesi",
        name="Paylaşım Bahçesi",
        type="Topluluk / Aile Alanı",
        description=(
            "Herkesin birlikte sebze-meyve yetiştirdiği, hasadı paylaştığı ortak bahçe."
        ),
        image_url="/static/locations/paylasim_bahcesi.png",
        ambient_video_url="/static/locations/videos/paylasim_bahcesi.mp4",
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
        ambient_video_url="/static/locations/videos/yildiz_tepesi.mp4",
    ),
    EpisodeLocation(
        location_id="gizli_magara",
        name="Gizli Mağara",
        type="Keşif / Gizem Alanı",
        description=(
            "Duvarlarında parıldayan kristallerin olduğu, sıcak ve büyülü ışıkla "
            "aydınlanan, korkutucu olmayan küçük bir mağara."
        ),
        image_url="/static/locations/gizli_magara.png",
        ambient_video_url="/static/locations/videos/gizli_magara.mp4",
    ),
    EpisodeLocation(
        location_id="renkli_cayir",
        name="Renkli Çayır",
        type="Sanat / Yaratıcılık Alanı",
        description=(
            "Her renkten kır çiçeğinin açtığı, kelebeklerin uçuştuğu, canlı ve "
            "ilham verici bir çayır."
        ),
        image_url="/static/locations/renkli_cayir.png",
        ambient_video_url="/static/locations/videos/renkli_cayir.mp4",
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
    EpisodeTheme(
        theme_id="durustluk",
        label="Dürüstlük",
        lead_character_id="zeytin",
        support_character_id="findik",
        location_id="buyuk_mese",
        lesson=(
            "Küçük bir yalan bile arkadaşlığı kırabilir; doğruyu söylemek başta zor "
            "gelse de içimizi hep rahatlatır."
        ),
    ),
    EpisodeTheme(
        theme_id="sabir",
        label="Sabır",
        lead_character_id="papatya",
        support_character_id="zeytin",
        location_id="paylasim_bahcesi",
        lesson=(
            "Güzel şeyler zamanla büyür; sabırla beklemeyi öğrenmek, sonunda en "
            "tatlı meyveyi toplamamızı sağlar."
        ),
    ),
    EpisodeTheme(
        theme_id="nezaket",
        label="Nezaket",
        lead_character_id="findik",
        support_character_id="minik",
        location_id="buyuk_mese",
        lesson="Küçük bir nazik söz veya davranış, bir günü baştan sona güzelleştirebilir.",
    ),
    EpisodeTheme(
        theme_id="ozguven",
        label="Özgüven",
        lead_character_id="minik",
        support_character_id="papatya",
        location_id="yildiz_tepesi",
        lesson=(
            "Herkesin kendine güvenmesi gereken bir yıldızı vardır; önemli olan o "
            "ışığı görebilmektir."
        ),
    ),
    EpisodeTheme(
        theme_id="sorumluluk",
        label="Sorumluluk",
        lead_character_id="boncuk",
        support_character_id="findik",
        location_id="buyuk_mese",
        lesson=(
            "Üstlendiğimiz küçük bir görevi bile tamamlamak, bize ve etrafımızdakilere "
            "güven verir."
        ),
    ),
    EpisodeTheme(
        theme_id="empati",
        label="Empati",
        lead_character_id="zeytin",
        support_character_id="minik",
        location_id="yildiz_tepesi",
        lesson="Bir başkasının yerine geçip onun gözünden bakmak, en büyük anlayış hediyesidir.",
    ),
    EpisodeTheme(
        theme_id="duzen",
        label="Düzen ve Temizlik",
        lead_character_id="papatya",
        support_character_id="boncuk",
        location_id="buyuk_mese",
        lesson=(
            "Etrafımızı düzenli tutmak, hem bizim hem de birlikte yaşadığımız "
            "arkadaşlarımızın işini kolaylaştırır."
        ),
    ),
    EpisodeTheme(
        theme_id="saglikli_beslenme",
        label="Sağlıklı Beslenme",
        lead_character_id="findik",
        support_character_id="papatya",
        location_id="paylasim_bahcesi",
        lesson=(
            "Renkli ve doğal besinler seçmek, güçlü ve enerjik kalmamızın en lezzetli "
            "yoludur."
        ),
    ),
    EpisodeTheme(
        theme_id="cevre_sevgisi",
        label="Doğayı Koruma",
        lead_character_id="zeytin",
        support_character_id="boncuk",
        location_id="gokkusagi_nehri",
        lesson="Doğa bize ev sahipliği yapar; onu temiz ve güvende tutmak hepimizin görevidir.",
    ),
    EpisodeTheme(
        theme_id="yaraticilik",
        label="Yaratıcılık",
        lead_character_id="boncuk",
        support_character_id="minik",
        location_id="gokkusagi_nehri",
        lesson=(
            "Bir sorunu çözmenin her zaman birden fazla yolu vardır; hayal gücümüzü "
            "kullanmaktan çekinmemeliyiz."
        ),
    ),
    EpisodeTheme(
        theme_id="farkliliklara_saygi",
        label="Farklılıklara Saygı",
        lead_character_id="findik",
        support_character_id="zeytin",
        location_id="paylasim_bahcesi",
        lesson=(
            "Herkesin farklı olması ormanı daha da renkli ve güzel yapar; "
            "farklılıklarımızla birbirimizi tamamlarız."
        ),
    ),
    EpisodeTheme(
        theme_id="yaratici_dusunme",
        label="Yaratıcı Düşünme",
        lead_character_id="kurnaz",
        support_character_id="papatya",
        location_id="gizli_magara",
        lesson=(
            "Bir sorunun tek bir çözümü yoktur; farklı düşünmek bazen en iyi "
            "yolu bulmamızı sağlar."
        ),
    ),
    EpisodeTheme(
        theme_id="kendini_kabul",
        label="Kendini Kabul Etme",
        lead_character_id="diken",
        support_character_id="minik",
        location_id="renkli_cayir",
        lesson=(
            "Farklı olmak eksiklik değildir; kendimiz olduğumuzda en güzel "
            "haldeyizdir."
        ),
    ),
    EpisodeTheme(
        theme_id="umut",
        label="Umut",
        lead_character_id="isik",
        support_character_id="boncuk",
        location_id="yildiz_tepesi",
        lesson=(
            "En karanlık anlarda bile küçük bir umut ışığı, yolumuzu bulmamıza "
            "yeter."
        ),
    ),
    EpisodeTheme(
        theme_id="degisime_uyum",
        label="Değişime Uyum Sağlama",
        lead_character_id="kurnaz",
        support_character_id="zeytin",
        location_id="gokkusagi_nehri",
        lesson=(
            "Değişim korkutucu görünebilir ama her yeni durum, yeni bir şey "
            "öğrenmek için bir fırsattır."
        ),
    ),
    EpisodeTheme(
        theme_id="sanatsal_ifade",
        label="Sanatsal İfade",
        lead_character_id="papatya",
        support_character_id="diken",
        location_id="renkli_cayir",
        lesson=(
            "Kendimizi anlatmanın bir sürü yolu vardır; resim, şarkı, dans... "
            "hepsi güzeldir."
        ),
    ),
    EpisodeTheme(
        theme_id="korkuyla_basetme",
        label="Korkuyla Baş Etme",
        lead_character_id="diken",
        support_character_id="minik",
        location_id="gizli_magara",
        lesson=(
            "Korkmak normaldir; önemli olan korkuyla birlikte küçük bir adım "
            "atabilmektir."
        ),
    ),
    EpisodeTheme(
        theme_id="liderlik",
        label="Liderlik ve Sorumluluk Alma",
        lead_character_id="kurnaz",
        support_character_id="boncuk",
        location_id="buyuk_mese",
        lesson=(
            "Lider olmak en çok konuşan değil, herkesi dinleyip doğru kararı "
            "bulan kişidir."
        ),
    ),
    EpisodeTheme(
        theme_id="dostluk_cesitliligi",
        label="Farklı Arkadaşlıklar Kurmak",
        lead_character_id="isik",
        support_character_id="findik",
        location_id="gokkusagi_nehri",
        lesson=(
            "Bazen en güzel dostluklar, hiç beklemediğimiz, bize hiç "
            "benzemeyen biriyle kurulur."
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
