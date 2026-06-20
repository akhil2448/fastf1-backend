TEAM_NAME_MAP = {
    "alfa romeo": "Alfa Romeo",
    "alfa romeo racing": "Alfa Romeo",
    "alphatauri": "AlphaTauri",
    "alpine": "Alpine",
    "alpine f1 team": "Alpine",
    "aston martin": "Aston Martin",
    "ferrari": "Ferrari",
    "force india": "Force India",
    "haas f1 team": "Haas",
    "haas": "Haas",
    "kick sauber": "Kick Sauber",
    "sauber": "Sauber",
    "mclaren": "McLaren",
    "mercedes": "Mercedes",
    "rb": "Racing Bulls",
    "rb f1 team": "Racing Bulls",
    "racing bulls": "Racing Bulls",
    "red bull": "Red Bull",
    "red bull racing": "Red Bull",
    "racing point": "Racing Point",
    "renault": "Renault",
    "toro rosso": "Toro Rosso",
    "williams": "Williams",
    "cadillac": "Cadillac",
    "cadillac f1 team": "Cadillac",
}

def normalize_team_name(team_name: str) -> str:
    if not team_name:
        return ""

    key = team_name.strip().lower()

    return TEAM_NAME_MAP.get(
        key,
        team_name.strip()
    )