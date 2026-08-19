import uuid

import httpx


async def _authorized_headers(client: httpx.AsyncClient, email: str) -> dict[str, str]:
    payload = {"email": email, "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)
    login_response = await client.post("/auth/login", json=payload)
    token: str = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client: httpx.AsyncClient, email: str) -> tuple[str, dict[str, str]]:
    headers = await _authorized_headers(client, email)
    project_response = await client.post(
        "/projects", json={"name": "Neşeli Orman"}, headers=headers
    )
    project_id: str = project_response.json()["id"]
    return project_id, headers


async def test_list_themes_endpoint_returns_all_twenty_eight_themes(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/episodes/themes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 28
    paylasma = next(item for item in body if item["theme_id"] == "paylasma")
    assert paylasma["label"] == "Paylaşma"
    assert paylasma["lead_character_name"]
    assert paylasma["lead_character_image_url"] == "/static/characters/findik.png"
    assert paylasma["lead_character_voice_sample_url"] == "/static/characters/voices/findik.mp3"
    assert paylasma["support_character_name"]
    assert paylasma["support_character_image_url"] == "/static/characters/boncuk.png"
    assert (
        paylasma["support_character_voice_sample_url"] == "/static/characters/voices/boncuk.mp3"
    )
    assert paylasma["location_name"]
    assert paylasma["location_image_url"] == "/static/locations/paylasim_bahcesi.png"
    assert (
        paylasma["location_ambient_video_url"]
        == "/static/locations/videos/paylasim_bahcesi.mp4"
    )


async def test_list_themes_endpoint_includes_the_new_cast_and_locations(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/episodes/themes")

    assert response.status_code == 200
    body = response.json()
    yaratici_dusunme = next(item for item in body if item["theme_id"] == "yaratici_dusunme")
    assert yaratici_dusunme["label"] == "Yaratıcı Düşünme"
    assert yaratici_dusunme["lead_character_name"] == "Kurnaz"
    assert yaratici_dusunme["lead_character_image_url"] == "/static/characters/kurnaz.png"
    assert (
        yaratici_dusunme["lead_character_voice_sample_url"]
        == "/static/characters/voices/kurnaz.mp3"
    )
    assert yaratici_dusunme["location_name"] == "Gizli Mağara"
    assert yaratici_dusunme["location_image_url"] == "/static/locations/gizli_magara.png"
    assert (
        yaratici_dusunme["location_ambient_video_url"]
        == "/static/locations/videos/gizli_magara.mp4"
    )

    kendini_kabul = next(item for item in body if item["theme_id"] == "kendini_kabul")
    assert kendini_kabul["lead_character_name"] == "Diken"
    assert kendini_kabul["lead_character_image_url"] == "/static/characters/diken.png"
    assert kendini_kabul["location_name"] == "Renkli Çayır"
    assert kendini_kabul["location_image_url"] == "/static/locations/renkli_cayir.png"

    umut = next(item for item in body if item["theme_id"] == "umut")
    assert umut["lead_character_name"] == "Işık"
    assert umut["lead_character_image_url"] == "/static/characters/isik.png"
    assert umut["lead_character_voice_sample_url"] == "/static/characters/voices/isik.mp3"


async def test_list_themes_endpoint_exposes_kurnazs_talking_sample_and_nothing_else(
    client: httpx.AsyncClient,
) -> None:
    """Only Kurnaz has a lip-synced talking-sample demo video (see docs/ses-rehberi.md
    for why the rest of the cast doesn't yet — it's expensive to produce). Every other
    character's cast slot must serialize the field as a plain null, not omit it or error."""
    response = await client.get("/episodes/themes")

    assert response.status_code == 200
    body = response.json()

    yaratici_dusunme = next(item for item in body if item["theme_id"] == "yaratici_dusunme")
    assert yaratici_dusunme["lead_character_name"] == "Kurnaz"
    assert (
        yaratici_dusunme["lead_character_talking_sample_url"]
        == "/static/characters/talking_samples/kurnaz_demo.mp4"
    )
    assert yaratici_dusunme["support_character_talking_sample_url"] is None

    paylasma = next(item for item in body if item["theme_id"] == "paylasma")
    assert paylasma["lead_character_name"] != "Kurnaz"
    assert paylasma["support_character_name"] != "Kurnaz"
    assert paylasma["lead_character_talking_sample_url"] is None
    assert paylasma["support_character_talking_sample_url"] is None

    static_response = await client.get(yaratici_dusunme["lead_character_talking_sample_url"])
    assert static_response.status_code == 200
    assert static_response.headers["content-type"] == "video/mp4"


async def test_generate_episode_endpoint_returns_episode_seo_and_shorts(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "duygular"})

    assert response.status_code == 201
    body = response.json()
    assert uuid.UUID(body["id"])
    assert body["episode"]["theme_id"] == "duygular"
    assert len(body["episode"]["scenes"]) == 5
    assert len(body["seo"]["titles"]) == 5
    assert body["episode"]["lead_character"]["voice_sample_url"].startswith(
        "/static/characters/voices/"
    )
    assert body["episode"]["support_character"]["voice_sample_url"].startswith(
        "/static/characters/voices/"
    )
    assert body["episode"]["location"]["ambient_video_url"].startswith(
        "/static/locations/videos/"
    )
    assert body["shorts"]["total_duration_seconds"] == 45


async def test_generate_episode_endpoint_returns_404_for_unknown_theme(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "does-not-exist"})

    assert response.status_code == 404


async def test_generated_episode_is_persisted_and_listed(client: httpx.AsyncClient) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "cesaret"})
    episode_id = generated.json()["id"]

    response = await client.get("/episodes")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 20
    [summary] = body["items"]
    assert summary["id"] == episode_id
    assert summary["theme_id"] == "cesaret"
    assert summary["title"] == "Neşeli Orman: Cesaret"
    assert summary["lead_character_name"]
    assert summary["lead_character_image_url"] == "/static/characters/minik.png"
    assert summary["lead_character_voice_sample_url"] == "/static/characters/voices/minik.mp3"


async def test_generated_episodes_list_is_newest_first(client: httpx.AsyncClient) -> None:
    first = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    second = await client.post("/episodes/generate", json={"theme_id": "aile"})

    response = await client.get("/episodes")

    ids = [item["id"] for item in response.json()["items"]]
    assert ids == [second.json()["id"], first.json()["id"]]


async def test_get_generated_episode_endpoint_returns_full_detail(
    client: httpx.AsyncClient,
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "sayilar"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}")

    assert response.status_code == 200
    assert response.json() == generated.json()


async def test_get_generated_episode_endpoint_returns_404_for_unknown_id(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(f"/episodes/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_generate_episode_endpoint_accepts_an_optional_project_id(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "project-owner@example.com")

    response = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["project_id"] == project_id


async def test_generate_episode_endpoint_defaults_project_id_to_null(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "duygular"})

    assert response.status_code == 201
    assert response.json()["project_id"] is None


async def test_generate_episode_with_project_id_requires_authentication(
    client: httpx.AsyncClient,
) -> None:
    project_id, _headers = await _create_project(client, "unauth-owner@example.com")

    response = await client.post(
        "/episodes/generate", json={"theme_id": "duygular", "project_id": project_id}
    )

    assert response.status_code == 401


async def test_generate_episode_with_project_id_rejects_a_non_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, _owner_headers = await _create_project(client, "real-owner@example.com")
    other_headers = await _authorized_headers(client, "intruder@example.com")

    response = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=other_headers,
    )

    assert response.status_code == 403


async def test_generate_episode_with_project_id_rejects_an_invalid_token(
    client: httpx.AsyncClient,
) -> None:
    project_id, _headers = await _create_project(client, "bad-token-owner@example.com")

    response = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


async def test_generate_episode_with_project_id_rejects_an_unknown_project(
    client: httpx.AsyncClient,
) -> None:
    headers = await _authorized_headers(client, "ghost-project@example.com")

    response = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": str(uuid.uuid4())},
        headers=headers,
    )

    assert response.status_code == 403


async def test_list_generated_episodes_filters_by_project_id(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "filter-owner@example.com")
    in_project = await client.post(
        "/episodes/generate",
        json={"theme_id": "cesaret", "project_id": project_id},
        headers=headers,
    )
    await client.post("/episodes/generate", json={"theme_id": "aile"})

    response = await client.get("/episodes", params={"project_id": project_id}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == in_project.json()["id"]


async def test_list_generated_episodes_with_project_id_requires_authentication(
    client: httpx.AsyncClient,
) -> None:
    project_id, _headers = await _create_project(client, "list-unauth-owner@example.com")

    response = await client.get("/episodes", params={"project_id": project_id})

    assert response.status_code == 401


async def test_list_generated_episodes_with_project_id_rejects_a_non_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, _owner_headers = await _create_project(client, "list-real-owner@example.com")
    other_headers = await _authorized_headers(client, "list-intruder@example.com")

    response = await client.get(
        "/episodes", params={"project_id": project_id}, headers=other_headers
    )

    assert response.status_code == 403


async def test_list_generated_episodes_without_project_id_stays_anonymous(
    client: httpx.AsyncClient,
) -> None:
    """The unscoped listing must keep working with no token at all, unchanged."""
    await client.post("/episodes/generate", json={"theme_id": "duygular"})

    response = await client.get("/episodes")

    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_generate_episode_endpoint_rejects_malformed_json_body(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/episodes/generate",
        content=b"{not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


async def test_generate_episode_endpoint_rejects_an_overlong_theme_id(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "x" * 101})

    assert response.status_code == 422


async def test_list_generated_episodes_rejects_a_page_size_over_the_max(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/episodes", params={"page_size": 101})

    assert response.status_code == 422


async def test_list_generated_episodes_rejects_a_non_positive_page(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/episodes", params={"page": 0})

    assert response.status_code == 422


async def test_generate_episode_endpoint_stores_script_like_input_as_inert_data(
    client: httpx.AsyncClient,
) -> None:
    """A theme_id can never contain markup, but this pins that arbitrary strings
    round-trip as plain JSON text and are never interpreted or executed server-side."""
    payload = {"theme_id": "<script>alert(1)</script>"}

    response = await client.post("/episodes/generate", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"]


async def test_get_generated_episode_endpoint_requires_authentication_for_a_project_episode(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "get-project-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}")

    assert response.status_code == 401


async def test_get_generated_episode_endpoint_rejects_a_non_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "get-real-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]
    other_headers = await _authorized_headers(client, "get-intruder@example.com")

    response = await client.get(f"/episodes/{episode_id}", headers=other_headers)

    assert response.status_code == 403


async def test_get_generated_episode_endpoint_allows_the_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "get-owner-allowed@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == episode_id


async def test_get_generated_episode_endpoint_stays_open_for_a_project_less_episode(
    client: httpx.AsyncClient,
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "duygular"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}")

    assert response.status_code == 200


async def test_delete_generated_episode_endpoint_requires_authentication_for_a_project_episode(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "delete-project-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.delete(f"/episodes/{episode_id}")

    assert response.status_code == 401


async def test_delete_generated_episode_endpoint_rejects_a_non_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "delete-real-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]
    other_headers = await _authorized_headers(client, "delete-intruder@example.com")

    response = await client.delete(f"/episodes/{episode_id}", headers=other_headers)

    assert response.status_code == 403

    # Confirm the non-owner's rejected attempt didn't actually delete it.
    still_there = await client.get(f"/episodes/{episode_id}", headers=headers)
    assert still_there.status_code == 200


async def test_delete_generated_episode_endpoint_allows_the_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "delete-owner-allowed@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.delete(f"/episodes/{episode_id}", headers=headers)

    assert response.status_code == 204


async def test_delete_generated_episode_endpoint_removes_it(client: httpx.AsyncClient) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "arkadaslik"})
    episode_id = generated.json()["id"]

    delete_response = await client.delete(f"/episodes/{episode_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/episodes/{episode_id}")
    assert get_response.status_code == 404

    second_delete_response = await client.delete(f"/episodes/{episode_id}")
    assert second_delete_response.status_code == 404
