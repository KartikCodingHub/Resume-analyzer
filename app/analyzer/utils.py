import re
from typing import List, Set, Tuple

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "for", "to", "from", "of",
    "in", "on", "with", "by", "as", "at", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "your", "our", "we", "you", "i", "me", "my",
    "us", "they", "them", "their", "he", "she", "his", "her", "hers", "him", "do", "does", "did",
    "will", "would", "should", "can", "could", "may", "might", "must", "not", "no", "yes",
}

ACTION_VERBS: Set[str] = {
    "achieved", "automated", "built", "consolidated", "created", "delivered", "designed", "developed",
    "drove", "enabled", "enhanced", "expanded", "founded", "implemented", "improved", "increased",
    "launched", "led", "migrated", "optimized", "orchestrated", "owned", "reduced", "refactored",
    "scaled", "shipped", "spearheaded", "streamlined", "transformed", "won",
}

MONTHS_PATTERN = r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
DATE_PATTERN = re.compile(rf"\b({MONTHS_PATTERN})\s+\d{{4}}|\b\d{{4}}\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"\+?\d[\d\s().-]{7,}\d")
LINK_PATTERN = re.compile(r"https?://[^\s)]+", re.IGNORECASE)
LINKEDIN_PATTERN = re.compile(r"https?://(www\.)?linkedin\.com/[^\s)]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"https?://(www\.)?github\.com/[^\s)]+", re.IGNORECASE)


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9+.#-]*", text.lower())


def filter_keywords(tokens: List[str], min_len: int = 3) -> List[str]:
    return [t for t in tokens if len(t) >= min_len and t not in STOPWORDS]


def count_sentences(text: str) -> int:
    parts = re.split(r"[.!?]+\s+", text.strip())
    parts = [p for p in parts if p]
    return max(1, len(parts))


def count_syllables(word: str) -> int:
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 1
    vowels = "aeiouy"
    syllables = 0
    prev_is_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            syllables += 1
        prev_is_vowel = is_vowel
    if word.endswith("e") and syllables > 1:
        syllables -= 1
    return max(1, syllables)


def basic_readability_flesch(text: str) -> float:
    tokens = tokenize(text)
    words = [t for t in tokens if t.isalpha()]
    num_words = max(1, len(words))
    num_sentences = count_sentences(text)
    num_syllables = sum(count_syllables(w) for w in words)
    # Flesch Reading Ease
    return 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)


def extract_contacts(text: str) -> Tuple[str, str, str, str]:
    email = EMAIL_PATTERN.search(text)
    phone = PHONE_PATTERN.search(text)
    linkedin = LINKEDIN_PATTERN.search(text) or LINK_PATTERN.search(text)
    github = GITHUB_PATTERN.search(text)
    return (
        email.group(0) if email else "",
        phone.group(0) if phone else "",
        linkedin.group(0) if linkedin else "",
        github.group(0) if github else "",
    )


def detect_sections(text: str) -> Tuple[set, set]:
    lines = [ln.strip().lower() for ln in text.splitlines() if ln.strip()]
    present = set()
    expected = {
        "summary", "objective", "experience", "work experience", "professional experience",
        "education", "skills", "projects", "certifications", "publications", "awards"
    }
    for ln in lines:
        for sec in list(expected):
            # consider a line a heading if it equals or starts with section keyword
            if ln == sec or ln.startswith(sec + ":"):
                present.add(sec)
    missing = expected - present
    return present, missing


def bullet_quality(text: str) -> Tuple[int, int, int, int]:
    lines = [ln.strip() for ln in text.splitlines()]
    bullet_lines = [ln for ln in lines if ln.startswith(("- ", "•", "* ", "– ", "— ", "· ", "o ", "• "))]
    num_bullets = len(bullet_lines)
    starts_with_action = 0
    first_person_count = 0
    numeric_impact = 0
    for ln in bullet_lines:
        first_word = ln.lstrip("-*•–—·o ").split(" ")[0].lower() if ln.lstrip("-*•–—·o ").split(" ") else ""
        if first_word in ACTION_VERBS:
            starts_with_action += 1
        if re.search(r"\b(I|me|my|we|our)\b", ln, re.IGNORECASE):
            first_person_count += 1
        if re.search(r"\b\d+%|\$\d+|\b\d{1,3}(?:,\d{3})*\b", ln):
            numeric_impact += 1
    return num_bullets, starts_with_action, first_person_count, numeric_impact