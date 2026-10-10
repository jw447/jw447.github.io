"""Shared publication display conventions for every demo."""


def publication_label(paper):
    """Use the concise venue abbreviation and two-digit publication year."""
    venue = paper['short'].removeprefix('IEEE ')
    return f"[{venue}'{str(paper['year'])[-2:]}]"
