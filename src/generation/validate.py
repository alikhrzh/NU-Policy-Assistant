import re

CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?!\[\d)|\n+")


def validate_citations(answer, source_count):
    numbers = set()
    for match in CITATION.findall(answer):
        numbers.update(int(number.strip()) for number in match.split(","))
    sentences = [part.strip() for part in SENTENCE_BOUNDARY.split(answer)]
    return {
        "citations": sorted(number for number in numbers if 1 <= number <= source_count),
        "invalid_citations": sorted(number for number in numbers if not 1 <= number <= source_count),
        "uncited_sentences": sum(
            any(character.isalpha() for character in sentence) and not CITATION.search(sentence)
            for sentence in sentences
        ),
    }
