"""
自动填充
"""
import json
import logging
from enum import Enum
from pathlib import Path
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent


class StaticBadgeTypes(Enum):
    FLAT = "flat"
    FLAT_SQUARE = "flat-square"
    PLASTIC = "plastic"
    FOR_THE_BADGE = "for-the-badge"
    SOCIAL = "social"


def clear_dict(d: dict) -> dict:
    res = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, str) and v.split() == "":
            continue
        if isinstance(v, list) and len(v) == 0:
            continue
        if isinstance(v, dict) and len(v.keys()) == 0:
            continue

        res[k] = v

    return res


def badge_content_url_escape(content: str) -> str:
    return quote(content.replace("-", "--").replace("_", "__"))


def gen_static_badge_content_str(label: str, message: str, color: str) -> str:
    label_escape = badge_content_url_escape(label)
    color_escape = quote(color)
    message_escape = badge_content_url_escape(message)

    return f"{label_escape}-{message_escape}-{color_escape}"


def gen_static_badge_query_params_str(params: dict) -> str:
    default_params = {
        "style": StaticBadgeTypes.FLAT.value,
        "logo": None,
        "logoColor": None,
        "label": None,
        "labelColor": None,
        "color": None,
        "cacheSeconds": None,
        "links": None,
    }
    allowed_keys = default_params.keys()
    for k, v in params.items():
        if k in allowed_keys:
            if k == "style":
                default_params[k] = StaticBadgeTypes[v].value
            else:
                default_params[k] = v
    clean_params = clear_dict(default_params)
    clean_params_str = urlencode(clean_params, doseq=False).replace("#", "")

    return clean_params_str


def gen_static_badge_url(
    label: str, message: str, color: str, query_params: dict | None = None
) -> str:
    if query_params is None:
        query_params = {}
    template = "https://img.shields.io/badge/{badgeContent}?{queryParams}"

    return template.format(
        **{
            "badgeContent": gen_static_badge_content_str(
                label=label, message=message, color=color
            ),
            "queryParams": gen_static_badge_query_params_str(query_params),
        }
    )


def gen_static_badge_markdown_link(
    label: str,
    message: str,
    color: str,
    query_params: dict | None = None,
) -> str:
    template = "![{label}]({url})"

    url = gen_static_badge_url(
        label=label, message=message, color=color, query_params=query_params
    )

    return template.format(label=label or message, url=url)


def batch_gen_static_badge_markdown_link(badges: list, sep: str = " ") -> str:
    new_list = []

    for badge in badges:
        if isinstance(badge, str):
            new_list += [badge]
        if isinstance(badge, dict):
            new_list += [gen_static_badge_markdown_link(**badge)]

    return sep.join(new_list)


def fill_skills(markdown_text: str, skills_config: dict) -> dict:
    ret = markdown_text

    # skills
    # skills language
    if "language" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.language>",
            batch_gen_static_badge_markdown_link(skills_config["language"]),
        )
    # skills tools & platform
    if "toolsAndPlatform" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.toolsAndPlatform>",
            batch_gen_static_badge_markdown_link(skills_config["toolsAndPlatform"]),
        )
    # skills IDE
    if "toolsAndPlatform" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.IDE>",
            batch_gen_static_badge_markdown_link(skills_config["IDE"]),
        )
    # skills knownledge
    if "knownledge" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.knownledge>",
            batch_gen_static_badge_markdown_link(skills_config["knownledge"]),
        )
    # skills CI/CD
    if "ciAndCd" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.ciAndCd>",
            batch_gen_static_badge_markdown_link(skills_config["ciAndCd"]),
        )
    # skills databases
    if "databases" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.databases>",
            batch_gen_static_badge_markdown_link(skills_config["databases"]),
        )
    # skills OS
    if "OS" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.OS>",
            batch_gen_static_badge_markdown_link(skills_config["OS"]),
        )
    # skills databases
    if "machineLearningAndDeepLearningFrameworks" in skills_config:
        ret = ret.replace(
            "<<placeholder> skills.machineLearningAndDeepLearningFrameworks>",
            batch_gen_static_badge_markdown_link(
                skills_config["machineLearningAndDeepLearningFrameworks"]
            ),
        )

    return ret


if __name__ == "__main__":
    # 读取配置文件
    with open(BASE_DIR / "config" / "config_skills.json", "r") as f:
        config_skills = json.load(f)
    # 读取模板文件
    with open(BASE_DIR / "template" / "README.template.md", "r") as f:
        readme_template = f.read()

    readme_text = readme_template
    # 填充 skills
    readme_text = fill_skills(readme_text, config_skills)

    with open(BASE_DIR / "README.md", "w") as f:
        f.write(readme_text)
