import requests
from typing import Any, Dict, List, Optional, Tuple
from data.scrapping import get_plant_uses, get_google_uses, get_plant_uses_family, watering_message, search_images_and_encode_first, \
    truncate_words, generate_category, get_plant_description_wikipedia


def normalize_plant_uses(plant_uses: Any) -> Tuple[Any, str]:
    """
    Normalize plant_uses into a data + type tuple so callers can render consistently.
    """
    if isinstance(plant_uses, set):
        return plant_uses, "set"
    if isinstance(plant_uses, dict):
        # Reverse item order for display (mimicking your original reversal)
        return dict(reversed(list(plant_uses.items()))), "dict"
    return plant_uses, type(plant_uses).__name__ if plant_uses is not None else "none"


def fetch_plant_info(access_token: str, headers: Dict[str, str], session: Optional[requests.Session] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch plant info from the Plant.id KB API. Returns parsed JSON dict or None on error.
    """
    if not access_token:
        return None
    url = (
        f"https://plant.id/api/v3/kb/plants/{access_token}"
        "?details=common_names,url,description,taxonomy,rank,gbif_id,"
        "inaturalist_id,image,synonyms,edible_parts,watering&language=en"
    )
    s = session or requests
    try:
        r = s.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        # You may want to log exc somewhere
        print(str(exc))
        return None


def choose_common_name(common_names: List[str], family: Optional[str], botanical_name: Optional[str]) -> List[str]:
    """
    Replace any common name that equals the family (case-insensitive) with the botanical name.
    Returns a possibly adjusted list of common names.
    """
    if not common_names:
        return []
    if not family or not botanical_name:
        return common_names
    adjusted = []
    fam_lower = family.lower()
    for cn in common_names:
        if cn and cn.lower() == fam_lower:
            adjusted.append(botanical_name)
        else:
            adjusted.append(cn)
    return adjusted


def resolve_plant_uses(
    common_names: List[str],
    botanical_name: Optional[str],
    family: Optional[str],
) -> Tuple[Any, List[str]]:
    """
    Try to resolve plant uses in order:
      1. For each common name (after family-name replacement), call get_plant_uses(cn, botanical_name).
      2. If none found, and we had at least one common name, call get_google_uses(common_names[0]).
      3. If still none, try get_plant_uses_family(family, botanical_name) if family available.
    Returns (plant_uses, possibly_updated_common_names).
    """
    adjusted_common_names = choose_common_name(common_names, family, botanical_name)
    plant_uses = None

    for cn in adjusted_common_names:
        plant_uses = get_plant_uses(cn, botanical_name)
        if plant_uses is not None:
            return plant_uses, adjusted_common_names

    if adjusted_common_names:
        plant_uses = get_google_uses(adjusted_common_names[0])
        if plant_uses is not None:
            return plant_uses, adjusted_common_names

    # Last resort: try by family
    if family and botanical_name:
        plant_uses, cn = get_plant_uses_family(family, botanical_name)
        if plant_uses is not None:
            return plant_uses, [cn] if cn else adjusted_common_names

    return None, adjusted_common_names


def build_plant_details_from_response(
    response,
    headers: Dict[str, str],
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    """
    Process the Plant.id response and enrich each entity with metadata, uses, and irrigation info.
    Returns a list of dicts:
      {
        'image_url': <data-uri string>,
        'plant_data': {
            'name': <botanical_name>,
            'common_name': < the best common name or None>,
            'taxonomy': <reversed taxonomy dict>,
            'description': <shortened description or None>,
            'edible_part': <edible parts>,
            'watering': <irrigation info string or None>,
        },
        'plant_uses': <normalized plant uses data>,
        'plant_uses_type': <'set'|'dict'|'none'|...>,
      }
    """
    data = response.json()
    entities = data.get("entities", [])
    if not entities:
        return []

    plant_details: List[Dict[str, Any]] = []

    for entity in entities:
        if entity.get("matched_in_type") == "synonym":
            continue

        access_token = entity.get("access_token")
        thumb_b64 = entity.get("thumbnail")
        image_url = f"data:image/jpeg;base64,{thumb_b64}" if thumb_b64 else None

        result = fetch_plant_info(access_token, headers, session=session)
        if not result:
            # Skip if we couldn't fetch plant info
            continue

        botanical_name = result.get("name")
        taxonomy = result.get("taxonomy") or {}
        family = taxonomy.get("family")

        # watering / irrigation
        watering = result.get("watering")
        irrigation_info = watering_message(watering) if watering else None

        # description
        description_obj = result.get("description") or {}
        description = description_obj.get("value")
        if description:
            description = truncate_words(description, 60)

        # edible parts
        edible_parts = result.get("edible_parts")

        # common names
        common_names = result.get("common_names") or []
        plant_uses_raw, common_names = resolve_plant_uses(common_names, botanical_name, family)

        # taxonomy reversed for display
        reversed_taxonomy = dict(reversed(list(taxonomy.items()))) if taxonomy else {}

        # pick best image — try search by first common name, else botanical name
        search_term = common_names[0] if common_names else botanical_name
        img_b64 = search_images_and_encode_first(search_term) if search_term else None
        if img_b64:
            image_url = f"data:image/jpeg;base64,{img_b64}"

        # normalize plant uses
        plant_uses, plant_uses_type = normalize_plant_uses(plant_uses_raw)

        plant_details.append(
            {
                "image_url": image_url,
                "plant_data": {
                    "name": botanical_name,
                    "common_name": common_names[0] if common_names else None,
                    "taxonomy": reversed_taxonomy,
                    "description": description,
                    "edible_part": edible_parts,
                    "watering": irrigation_info,
                },
                "plant_uses": plant_uses,
                "plant_uses_type": plant_uses_type,
            }
        )

    return plant_details


def _normalize_saved_plant_uses(raw):
    """
    Normalize plant_uses loaded from DB.
    Returns (plant_uses_display, plant_uses_type).
    """
    if isinstance(raw, set):
        # You can also sort(raw) if you want deterministic order in templates
        return raw, "set"
    if isinstance(raw, dict):
        # Reverse order as in your original code
        return dict(reversed(list(raw.items()))), "dict"
    return raw, ("none" if raw is None else type(raw).__name__)


def _cap(s):
    return s.capitalize() if isinstance(s, str) else s


def _extract_disease_info(result):
    """
    Pull disease info from Plant.id result payload.
    Returns tuple: (category, description, common_name, disease_name)
    """
    disease_block = result.get("disease") or {}
    suggestions = disease_block.get("suggestions") or []
    if not suggestions:
        return "", "None", "None", "None"

    d = suggestions[0]
    prob = d.get("probability", 0)
    category = generate_category(prob)  # your helper

    d_details = d.get("details") or {}
    description = d_details.get("description") or "None"
    d_common_names = d_details.get("common_names") or []
    common_name = d_common_names[0] if d_common_names else "None"

    disease_name = d.get("name") or "None"
    return category, description, common_name, disease_name


def _extract_classification_core(result):
    """
    Extracts classification summary:
    Returns (plant_name, common_name, taxonomy_dict, description, edible_parts, watering)
    Handles fallback to 2nd suggestion and to Wikipedia when needed.
    """
    classification = result.get("classification") or {}
    suggestions = classification.get("suggestions") or []
    top = suggestions[0] if suggestions else {}
    top_details = top.get("details") or {}

    common_names = top_details.get("common_names") or []
    plant_name = top.get("name")

    # Fallback: 2nd suggestion if no common names
    alt_details = None
    if not common_names and len(suggestions) > 1:
        alt = suggestions[1]
        alt_details = alt.get("details") or {}
        common_names = alt_details.get("common_names") or []
        plant_name = alt.get("name", plant_name)

    # Choose common name
    common_name = common_names[0] if common_names else None

    # Taxonomy
    taxonomy = top_details.get("taxonomy") or {}
    # If top had nothing, and we fell back to alt suggestion
    if not taxonomy and alt_details is not None:
        taxonomy = alt_details.get("taxonomy") or {}
    reversed_taxonomy = dict(reversed(list(taxonomy.items()))) if taxonomy else {}

    # Description
    desc_obj = top_details.get("description") or {}
    description = desc_obj.get("value")
    if not description and alt_details is not None:
        description = (alt_details.get("description") or {}).get("value")
    if not description:
        # Wikipedia fallback(s)
        if common_name:
            description = get_plant_description_wikipedia(common_name)
        if not description and plant_name:
            description = get_plant_description_wikipedia(plant_name)
    if not description:
        description = "Description not available."

    # Edible parts
    edible_parts = top_details.get("edible_parts")
    if edible_parts is None and alt_details is not None:
        edible_parts = alt_details.get("edible_parts")

    # Watering
    watering = top_details.get("watering")
    if watering is None and alt_details is not None:
        watering = alt_details.get("watering")

    return plant_name, common_name, reversed_taxonomy, description, edible_parts, watering
