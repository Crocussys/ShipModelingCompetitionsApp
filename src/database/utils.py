def make_short_name(full_name: str) -> str:
    parts = full_name.strip().split()

    if len(parts) < 2:
        return full_name.strip()

    surname = parts[0]
    initials = ""

    for part in parts[1:]:
        initials += f"{part[0]}."

    return f"{surname} {initials}"
