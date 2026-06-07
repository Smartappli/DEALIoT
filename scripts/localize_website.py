"""Generate localized static website pages from the English canonical page."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DIR = REPO_ROOT / "website"
BASE_URL = "https://smartappli.io/"
ASSET_VERSION = "20260607-language-dropdown-v2"
TRANSLATION_FILE = WEBSITE_DIR / "src" / "i18n-copy.json"


LANGUAGES = {
    "bg": {"path": "bg", "og_locale": "bg_BG"},
    "hr": {"path": "hr", "og_locale": "hr_HR"},
    "cs": {"path": "cs", "og_locale": "cs_CZ"},
    "da": {"path": "da", "og_locale": "da_DK"},
    "nl": {"path": "nl", "og_locale": "nl_NL"},
    "et": {"path": "et", "og_locale": "et_EE"},
    "fi": {"path": "fi", "og_locale": "fi_FI"},
    "fr": {"path": "fr", "og_locale": "fr_FR"},
    "de": {"path": "de", "og_locale": "de_DE"},
    "el": {"path": "el", "og_locale": "el_GR"},
    "hu": {"path": "hu", "og_locale": "hu_HU"},
    "ga": {"path": "ga", "og_locale": "ga_IE"},
    "it": {"path": "it", "og_locale": "it_IT"},
    "lv": {"path": "lv", "og_locale": "lv_LV"},
    "lt": {"path": "lt", "og_locale": "lt_LT"},
    "mt": {"path": "mt", "og_locale": "mt_MT"},
    "pl": {"path": "pl", "og_locale": "pl_PL"},
    "pt": {"path": "pt", "og_locale": "pt_PT"},
    "ro": {"path": "ro", "og_locale": "ro_RO"},
    "sk": {"path": "sk", "og_locale": "sk_SK"},
    "sl": {"path": "sl", "og_locale": "sl_SI"},
    "es": {"path": "es", "og_locale": "es_ES"},
    "sv": {"path": "sv", "og_locale": "sv_SE"},
}


ENGLISH = {
    "meta_description": "DEAL presents DEALIoT, DEALHost and DEALData: a production-ready IoT data platform, managed hosting path and data governance layer for scalable field data ecosystems.",
    "keywords": "DEALIoT, DEALHost, DEALData, IoT data platform, Kafka, Flink, Kubernetes, data governance, managed hosting",
    "og_description": "A professional IoT data suite for real-time ingestion, operated infrastructure and governed data sharing.",
    "twitter_description": "Real-time IoT ingestion, operated hosting and governed data products with compliance evidence.",
    "og_image_alt": "DEALIoT, DEALHost and DEALData for scalable IoT data ecosystems.",
    "twitter_image_alt": "DEAL suite public website preview.",
    "website_description": "Public website for the DEAL suite: DEALIoT, DEALHost and DEALData.",
    "app_category": "IoT data platform",
    "dealiot_schema_description": "DEALIoT ingests IoT telemetry and media metadata through MQTT, Kafka, Apicurio, Flink, Beam, Airflow, Prometheus and Grafana.",
    "dealhost_schema_description": "DEALHost is the operated hosting path for DEAL workloads on hardened cloud, hybrid or on-prem infrastructure.",
    "dealhost_schema_service_type": "Managed data platform hosting",
    "dealdata_schema_description": "DEALData structures catalogues, controlled sharing, exports, Data Act evidence, DGA workflows, FAIR publication, Zenodo and OpenAIRE.",
    "dealdata_schema_service_type": "Data governance and sharing",
    "suite_schema_description": "DEAL suite combines IoT ingestion, operated hosting and governed data products.",
    "faq_schema_dealhost": "DEALHost is the hosting and operations path for running DEAL workloads on Kubernetes, cloud, hybrid or on-prem infrastructure.",
    "faq_schema_dealdata": "DEALData is the governance layer for catalogues, controlled sharing, exports and Data Act, DGA and FAIR evidence.",
    "skip": "Skip to content",
    "deal_home": "DEAL home",
    "tagline": "Data ecosystems that scale",
    "primary_nav": "Primary navigation",
    "nav_products": "Products",
    "nav_platform": "Platform",
    "nav_proof": "Proof",
    "nav_adoption": "Adoption",
    "nav_faq": "FAQ",
    "nav_contact": "Contact",
    "choose_language": "Choose language",
    "star": "Star on GitHub",
    "request_demo": "Request a demo",
    "hero_eyebrow": "DEALIoT + DEALHost + DEALData",
    "h1": "Operate field data like a production system.",
    "hero_lede": "DEAL brings DEALIoT, DEALHost and DEALData together for IoT telemetry, operated infrastructure and governed data sharing.",
    "explore_suite": "Explore the suite",
    "see_platform": "See the platform",
    "platform_promises": "Platform promises",
    "coordinated_products": "coordinated products",
    "operations_view": "operations view",
    "compliance_evidence": "compliance evidence",
    "suite_overview": "DEAL suite overview",
    "operate_data_trust": "Operate data with trust",
    "products_eyebrow": "One suite, three adoption paths",
    "build_host_govern": "Build, host and govern.",
    "products_intro": "Each product can be adopted independently. Together, they cover the full cycle from field ingestion to operated infrastructure, governance and controlled data sharing.",
    "dealiot_desc": "Real-time IoT platform for sensors, media metadata and industrial streams. MQTT, Kafka, Flink, Airflow and Kubernetes are assembled to move from prototype to scalable operations.",
    "dealiot_li1": "MQTT to Kafka ingestion",
    "dealiot_li2": "Stream processing and backfill",
    "dealiot_li3": "Integrated observability and DLQ",
    "dealhost_desc": "Operated hosting for critical data workloads: Kubernetes, object storage, monitoring, backups, hardening and continuous operations.",
    "dealhost_li1": "Secured application clusters",
    "dealhost_li2": "Runbooks, alerts and backups",
    "dealhost_li3": "Cloud, hybrid or on-prem paths",
    "dealdata_desc": "Governance and value layer: catalogues, evidence topics, controlled exports, Data Act, DGA, FAIR, Zenodo and OpenAIRE.",
    "dealdata_li1": "Catalogues and data products",
    "dealdata_li2": "Controlled sharing and traceability",
    "dealdata_li3": "Usable compliance evidence",
    "target_platform": "Target platform",
    "open_foundation": "An open foundation that avoids vendor lock-in.",
    "capture": "Capture",
    "capture_desc": "Connected devices, WildFi, MQTT gateways and media producers.",
    "transport": "Transport",
    "transport_desc": "Kafka, schema registry, business topics, DLQ and event contracts.",
    "operate": "Operate",
    "operate_desc": "Kubernetes, DEALHost, observability, security and SLOs.",
    "value": "Value",
    "value_desc": "DEALData, catalogues, exports, compliance evidence and controlled sharing.",
    "why_adopt": "Why adopt",
    "difference": "The difference: an auditable architecture before production.",
    "proof_desc": "The DEAL suite does not only sell a diagram. It provides manifests, tests, workflows, runbooks, security evidence and documentation that reduce adoption risk.",
    "tests": "Tests",
    "ci_guardrails": "CI/CD guardrails",
    "ci_desc": "Unit, integration, deployment, Kustomize, Swarm and supply-chain validation.",
    "scalability": "Scalability",
    "horizontal_design": "Horizontal by design",
    "scale_desc": "Shared MQTT subscriptions, Kafka partitions, Flink task managers, HPA and PDB.",
    "trust": "Trust",
    "dedicated_topics": "Dedicated topics for governance, security, resilience and European obligations.",
    "adoption_path": "Adoption path",
    "public_path": "A public path to evaluate without friction.",
    "adoption_desc": "The DEAL suite exposes a clear path: test locally, scope a 30-day pilot, document integrations and contribute without breaking production guardrails.",
    "evaluate": "Evaluate",
    "reproducible_demo": "Reproducible demo",
    "eval_desc": "Run the smoke test, choose one field stream, measure the first usable event and capture decision evidence.",
    "read_playbook": "Read the pilot playbook",
    "contribute": "Contribute",
    "structured_community": "Structured community",
    "community_desc": "Discussions, feedback forms, support rules, community rituals and roadmap triage make user adoption readable and maintainable.",
    "community_plan": "Community plan",
    "integrate": "Integrate",
    "partners_use_cases": "Partners and use cases",
    "usecase_desc": "Concrete livestock, research, agriculture, industrial, publication and partner scenarios make fit easier to validate.",
    "use_case_catalog": "Use case catalog",
    "decide": "Decide",
    "champion_decision_kit": "Champion decision kit",
    "decision_kit_desc": "Comparison, quick evaluation and internal champion materials help teams convert interest into a measured adoption decision.",
    "open_decision_kit": "Open the decision kit",
    "develop": "Develop",
    "contributor_community": "Contributor community",
    "contributor_community_desc": "Contribution tracks, mentoring labels, governance rules and contributor help discussions make development support easier to join.",
    "start_contributing": "Start contributing",
    "direct_answers": "Direct answers",
    "short_answers": "Short answers for fast evaluation.",
    "faq_intro": "This section gives decision-makers, integrators and answer engines the canonical definitions of DEALIoT, DEALHost and DEALData.",
    "q_dealiot": "What is DEALIoT?",
    "a_dealiot": "DEALIoT is a production-oriented IoT data platform for MQTT ingestion, Kafka transport, schema governance, stream processing, backfill and operational evidence.",
    "q_dealhost": "What is DEALHost?",
    "a_dealhost": "DEALHost operates the DEAL suite on hardened infrastructure: Kubernetes, monitoring, backups, runbooks, security and support boundaries.",
    "q_dealdata": "What is DEALData?",
    "a_dealdata": "DEALData structures catalogues, data products, controlled sharing, FAIR exports, Zenodo, OpenAIRE and Data Act or Data Governance Act evidence.",
    "q_eval": "How do I start an evaluation?",
    "a_eval": "The recommended path is to run the local smoke test, choose one representative field stream, scope a 30-day pilot and score the evidence before production.",
    "q_usecases": "Which use cases fit?",
    "a_usecases": "The suite targets research teams, precision agriculture, connected livestock, industrial IoT, public projects and integrators that must industrialize field data.",
    "q_compliance": "Is the platform compliance-certified?",
    "a_compliance": "The repository provides compliance evidence, workflows, topics and templates. These assets support audits, but do not replace organization-specific certification.",
    "start_pilot": "Start a pilot",
    "measurable": "A measurable first use case in 30 days.",
    "launch_desc": "Select a field stream, define value indicators, deploy the pilot chain and measure time to the first usable event.",
    "contact_team": "Contact the team",
    "open_repo": "Open the GitHub repository",
    "deal_ecosystem": "DEAL ecosystem",
    "llms_context": "LLMS context",
}


def load_translations() -> dict[str, dict[str, str]]:
    data = json.loads(TRANSLATION_FILE.read_text(encoding="utf-8"))
    return cast("dict[str, dict[str, str]]", data)


def localized_url(path: str) -> str:
    return f"{BASE_URL}{path}/"


def apply_translations(html: str, lang: str, copy: dict[str, str]) -> str:
    html = html.replace(
        '<span><a href="https://smartappli.io/fr/" hreflang="fr" lang="fr">Français</a> / <a href="https://smartappli.io/llms.txt">LLMS context</a></span>',
        f'<span><a href="https://smartappli.io/" hreflang="en-US" lang="en-US">English</a> / <a href="https://smartappli.io/llms.txt">{copy["llms_context"]}</a></span>',
    )

    replacements = {ENGLISH[key]: value for key, value in copy.items() if key in ENGLISH}
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        html = html.replace(source, target)

    config = LANGUAGES[lang]
    path = config["path"]
    url = localized_url(path)

    html = html.replace('<html lang="en-US">', f'<html lang="{lang}">')
    html = html.replace(
        '<link rel="canonical" href="https://smartappli.io/">',
        f'<link rel="canonical" href="{url}">',
    )
    html = html.replace(
        '<meta property="og:url" content="https://smartappli.io/">',
        f'<meta property="og:url" content="{url}">',
    )
    html = html.replace(
        '<meta property="og:locale" content="en_US">',
        f'<meta property="og:locale" content="{config["og_locale"]}">',
    )
    html = html.replace(
        '<meta property="og:locale:alternate" content="fr_FR">',
        '<meta property="og:locale:alternate" content="en_US">',
    )
    html = html.replace('"inLanguage": "en-US"', f'"inLanguage": "{lang}"')

    html = html.replace('href="assets/', 'href="../assets/')
    html = html.replace('href="site.webmanifest"', 'href="../site.webmanifest"')
    html = html.replace('href="humans.txt"', 'href="../humans.txt"')
    html = html.replace(
        f'href="styles.css?v={ASSET_VERSION}"', f'href="../styles.css?v={ASSET_VERSION}"'
    )
    html = html.replace(f'src="app.js?v={ASSET_VERSION}"', f'src="../app.js?v={ASSET_VERSION}"')

    html = html.replace(
        '<option value="https://smartappli.io/" lang="en-US" selected>',
        '<option value="https://smartappli.io/" lang="en-US">',
    )
    return html.replace(
        f'<option value="{url}" lang="{lang}">', f'<option value="{url}" lang="{lang}" selected>'
    )


def main() -> None:
    translations = load_translations()
    missing_languages = set(LANGUAGES) - set(translations)
    if missing_languages:
        message = f"Missing translations: {sorted(missing_languages)}"
        raise SystemExit(message)

    template = (WEBSITE_DIR / "index.html").read_text(encoding="utf-8")
    for lang, config in LANGUAGES.items():
        copy = translations[lang]
        missing_keys = set(ENGLISH) - set(copy)
        if missing_keys:
            message = f"{lang} missing keys: {sorted(missing_keys)}"
            raise SystemExit(message)
        output = apply_translations(template, lang, copy)
        target_dir = WEBSITE_DIR / config["path"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(output, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
