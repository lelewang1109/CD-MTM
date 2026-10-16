"""Public method names; saved experimental keys remain unchanged."""
NAME = "RG-MTM"
FULL_NAME = "Reference-Guided Merge Tree Maps"
METHOD_LABELS = {
    "A": "RG-MTM-P",
    "A_full_hierarchy": "RG-MTM-P",
    "R 2%": "RG-MTM-R (κ=2%)",
    "R 20%": "RG-MTM-R",
    "R inf": "RG-MTM-R (κ=∞)",
    "R_relaxed": "RG-MTM-R",
    "CD-MTM": "RG-MTM-R",
}


def method_label(key):
    return METHOD_LABELS.get(key, key)
