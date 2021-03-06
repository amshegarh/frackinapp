from asyncio import gather

from src.git.get_files_common import GitFetcher


class ItemsFetcher(GitFetcher):
    root_folder = "items"
    allowed_files = (
        '.item', ".chest", ".head", ".legs", ".currency", ".thrownitem", ".activeitem", ".augment", ".back",
        ".beamaxe", ".consumable", ".flashlight", ".harvestingtool", ".instrument", ".liqitem", ".matitem",
        ".miningtool", ".tillingtool", ".wiretool"
    )
    entity_name_key = "itemName"


class RecipesFetcher(GitFetcher):
    root_folder = "recipes"
    allowed_files = (
        '.item', '.recipe'
    )


class MissionsFetcher(GitFetcher):
    root_folder = "ai"
    allowed_files = (
        '.aimission'
    )
    entity_name_key = "missionName"


class QuestsFetcher(GitFetcher):
    root_folder = "quests"
    allowed_files = (
        '.questtemplate'
    )
    entity_name_key = "id"


class CodexFetcher(GitFetcher):
    root_folder = "codex"
    allowed_files = (
        ".codex"
    )
    entity_name_key = "id"


class CollectionsFetcher(GitFetcher):
    root_folder = "collections"
    allowed_files = (
        ".collection"
    )
    entity_name_key = "name"


class BiomesFetcher(GitFetcher):
    root_folder = "biomes"
    allowed_files = (
        ".biome"
    )
    entity_name_key = "name"


class ObjectsFetcher(GitFetcher):
    root_folder = "objects"
    allowed_files = (
        '.object'
    )
    entity_name_key = "objectName"


class PlantsFetcher(GitFetcher):
    root_folder = "plants"
    allowed_files = (
        '.modularfoliage',
        '.modularstem'
    )
    entity_name_key = "name"


# status effects
class StatsFetcher(GitFetcher):
    root_folder = "stats"
    allowed_files = (
        '.statuseffect'
    )
    entity_name_key = "name"


class TechFetcher(GitFetcher):
    root_folder = "tech"
    allowed_files = (
        '.tech'
    )
    entity_name_key = "name"


class TenantsFetcher(GitFetcher):
    root_folder = "tenants"
    allowed_files = (
        '.tenant'
    )
    entity_name_key = "name"


async def get_all_fetchers(commit_id):
    return await gather(
        BiomesFetcher(commit_id=commit_id).fetch_data(),
        CodexFetcher(commit_id=commit_id).fetch_data(),
        CollectionsFetcher(commit_id=commit_id).fetch_data(),
        MissionsFetcher(commit_id=commit_id).fetch_data(),
        ObjectsFetcher(commit_id=commit_id).fetch_data(),
        PlantsFetcher(commit_id=commit_id).fetch_data(),
        QuestsFetcher(commit_id=commit_id).fetch_data(),
        RecipesFetcher(commit_id=commit_id).fetch_data(),
        StatsFetcher(commit_id=commit_id).fetch_data(),
        TenantsFetcher(commit_id=commit_id).fetch_data(),
        TechFetcher(commit_id=commit_id).fetch_data(),
        ItemsFetcher(commit_id=commit_id).fetch_data(),
    )