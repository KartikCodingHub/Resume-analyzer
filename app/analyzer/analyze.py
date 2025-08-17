import os
from typing import Dict, List, Tuple

try:
    import textstat  # type: ignore
except Exception:  # pragma: no cover
    textstat = None

from app.analyzer.utils import (
    clean_text,
    tokenize,
    filter_keywords,
    basic_readability_flesch,
    extract_contacts,
    detect_sections,
    bullet_quality,
    DATE_PATTERN,
)
from app.analyzer.skills_list import COMMON_SKILLS


def _readability_score(text: str) -> float:
    if textstat is not None:
        try:
            # textstat returns Flesch Reading Ease (higher is easier)
            return float(textstat.flesch_reading_ease(text))
        except Exception:
            pass
    return basic_readability_flesch(text)


def _normalize_score(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    clamped = max(min_val, min(max_val, value))
    return (clamped - min_val) / (max_val - min_val)


def _extract_skills(tokens: List[str]) -> List[str]:
    token_text = " ".join(tokens)
    found = set()
    for skill in COMMON_SKILLS:
        if skill in token_text:
            found.add(skill)
    # Also include single-token exact matches
    for tok in tokens:
        if tok in COMMON_SKILLS:
            found.add(tok)
    return sorted(found)


def _keyword_coverage(resume_tokens: List[str], job_description: str) -> Tuple[float, List[str], List[str], List[str]]:
    if not job_description or len(job_description.strip()) == 0:
        return 0.0, [], [], []
    jd_tokens = filter_keywords(tokenize(job_description))
    resume_token_set = set(resume_tokens)

    # Frequency-based top JD keywords
    freq: Dict[str, int] = {}
    for t in jd_tokens:
        freq[t] = freq.get(t, 0) + 1
    sorted_keywords = [k for k, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)]
    # Keep a focused set of top keywords
    jd_keywords = [k for k in sorted_keywords if len(k) >= 3][:40]

    found = [k for k in jd_keywords if k in resume_token_set]
    missing = [k for k in jd_keywords if k not in resume_token_set]
    coverage = (len(found) / max(1, len(jd_keywords))) * 100.0

    # Top missing: prioritize harder skills (tech/common skills intersection) with higher jd freq
    top_missing = missing[:10]
    return coverage, found, missing, top_missing


def _length_score(words_count: int) -> float:
    # Ideal range roughly 400-900 words for a 1-2 page resume
    if words_count < 250:
        return 0.3
    if 250 <= words_count <= 1100:
        return 1.0
    if 1100 < words_count <= 1500:
        return 0.6
    return 0.3


def analyze_resume_text(resume_text: str, job_description: str = "") -> Dict:
    text = clean_text(resume_text)

    # Contacts
    email, phone, linkedin, github = extract_contacts(text)

    # Sections
    present_sections, missing_sections = detect_sections(text)

    # Bullets
    num_bullets, starts_with_action, first_person_count, numeric_impact = bullet_quality(text)

    # Dates heuristic (employment timeline hints)
    dates = DATE_PATTERN.findall(text)

    # Tokenization and skills
    tokens = filter_keywords(tokenize(text))
    skills = _extract_skills(tokens)

    # Keyword coverage vs JD
    coverage, found_keywords, missing_keywords, top_missing = _keyword_coverage(tokens, job_description)

    # Readability
    reading_ease = _readability_score(text)
    clarity_score = _normalize_score(reading_ease, min_val=30.0, max_val=80.0)  # 0..1

    # Length
    words_count = len(tokens)
    length_score = _length_score(words_count)

    # Structure score: presence of key sections
    structure_components = [
        "experience" in present_sections or "work experience" in present_sections or "professional experience" in present_sections,
        "education" in present_sections,
        "skills" in present_sections,
        ("summary" in present_sections or "objective" in present_sections),
    ]
    structure_score = sum(1 for c in structure_components if c) / len(structure_components)

    # ATS-friendliness heuristic
    ats_components = [
        len(email) > 0,
        len(phone) > 0,
        num_bullets >= 5,
        starts_with_action >= max(1, int(num_bullets * 0.4)),
        first_person_count <= max(0, int(num_bullets * 0.1)),
        numeric_impact >= max(1, int(num_bullets * 0.2)),
        len(dates) >= 2,
    ]
    ats_score = sum(1 for c in ats_components if c) / len(ats_components)

    # Keyword score
    keyword_score = coverage / 100.0

    # Weighted overall score
    overall = (
        0.30 * structure_score +
        0.30 * keyword_score +
        0.20 * clarity_score +
        0.10 * length_score +
        0.10 * ats_score
    ) * 100.0

    # Suggestions
    suggestions: List[str] = []

    if not ("experience" in present_sections or "work experience" in present_sections or "professional experience" in present_sections):
        suggestions.append("Add a clear Experience section with company, title, location, and dates.")
    if "education" not in present_sections:
        suggestions.append("Include an Education section (degree, institution, graduation year).")
    if "skills" not in present_sections:
        suggestions.append("Add a Skills section listing relevant tools, languages, and frameworks.")
    if "summary" not in present_sections and "objective" not in present_sections:
        suggestions.append("Add a concise Summary at the top tailored to the target role.")

    if num_bullets < 8:
        suggestions.append("Use concise bullet points for achievements; aim for at least 8 impactful bullets across roles.")
    if starts_with_action < max(1, int(num_bullets * 0.4)):
        suggestions.append("Start bullets with strong action verbs (e.g., ‘Led’, ‘Built’, ‘Improved’).")
    if first_person_count > max(0, int(num_bullets * 0.1)):
        suggestions.append("Avoid first-person pronouns in bullets; keep phrasing objective.")
    if numeric_impact < max(1, int(num_bullets * 0.2)):
        suggestions.append("Quantify impact with metrics (%, $, time saved, scale).")

    if words_count < 250:
        suggestions.append("Resume may be too brief; expand with measurable achievements.")
    elif words_count > 1200:
        suggestions.append("Resume may be too long; tighten language and remove older/unrelated items.")

    if reading_ease < 40:
        suggestions.append("Improve readability with shorter sentences and simpler wording.")

    if len(missing_keywords) > 0 and job_description.strip():
        suggestions.append("Incorporate relevant job keywords naturally (avoid stuffing): " + ", ".join(top_missing[:5]))

    warnings: List[str] = []
    if len(email) == 0:
        warnings.append("No email detected; add a professional email address.")
    if len(phone) == 0:
        warnings.append("No phone number detected; add a reachable phone number.")
    if len(dates) < 2:
        warnings.append("Few date markers found; ensure roles include dates like ‘Jan 2021 – Present’.")

    # Optional: augment with LLM suggestions if available
    augmented_suggestions = _augment_with_llm_if_available(text, job_description)
    suggestions.extend(augmented_suggestions)

    # Assemble response
    response: Dict = {
        "score": round(overall, 1),
        "scores": {
            "structure": round(structure_score * 100, 1),
            "keywords": round(keyword_score * 100, 1),
            "clarity": round(clarity_score * 100, 1),
            "length": round(length_score * 100, 1),
            "ats": round(ats_score * 100, 1),
        },
        "highlights": {
            "contacts": {
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "github": github,
            },
            "sectionsPresent": sorted(list(present_sections)),
            "sectionsMissing": sorted(list(missing_sections)),
            "skills": skills,
            "wordCount": words_count,
            "readingEase": round(reading_ease, 1),
            "bulletStats": {
                "bullets": num_bullets,
                "actionVerbStarts": starts_with_action,
                "firstPersonBullets": first_person_count,
                "numericImpactBullets": numeric_impact,
            },
        },
        "keywordAnalysis": {
            "coverage": round(coverage, 1),
            "found": found_keywords,
            "missing": missing_keywords,
            "topMissing": top_missing,
        },
        "warnings": warnings,
        "suggestions": suggestions[:20],  # keep concise
    }

    return response


def _augment_with_llm_if_available(resume_text: str, job_description: str) -> List[str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    try:
        import importlib
        openai_spec = importlib.util.find_spec("openai")
        if openai_spec is None:
            return []
        import openai  # type: ignore

        client = openai.OpenAI(api_key=api_key)
        prompt = (
            "Give 5 concise, concrete suggestions to improve the following resume for the job description. "
            "Avoid fluff; focus on measurable impact, relevant keywords, and structure.\n\n"
            f"Resume:\n{resume_text[:6000]}\n\nJob Description:\n{job_description[:4000]}\n"
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert resume coach."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=256,
        )
        text = completion.choices[0].message.content or ""
        # Split into bullet-like suggestions
        lines = [ln.strip("- •* \t") for ln in text.splitlines() if ln.strip()]
        # Keep short lines
        return [ln for ln in lines if len(ln) <= 220][:5]
    except Exception:
        return []