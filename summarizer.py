import os
import re
from collections import Counter


STOPWORDS = {
    "경우",
    "그다음",
    "그다음에",
    "이렇게",
    "저렇게",
    "대한",
    "대해",
    "것들",
    "뭔지",
    "결국",
    "인제",
    "이제",
    "그래서",
    "그리고",
    "그러면",
    "그런데",
    "하지만",
    "때문에",
    "같은",
    "어떤",
    "우리가",
    "이거",
    "저거",
    "여기",
    "저기",
    "거기",
    "하나",
    "정도",
    "한번",
    "조금",
    "많이",
    "계속",
    "다시",
    "바로",
    "그냥",
    "되다",
    "하다",
    "있다",
    "없다",
    "같다",
    "보다",
    "말하다",
    "설명",
    "내용",
    "내용들",
    "가지",
    "문제",
    "방법",
    "개념",
    "기본",
    "중요",
    "필요",
    "발생",
    "관련",
    "그리고요",
    "그러니까",
    "뭐냐",
    "뭔가",
    "약간",
    "정말",
    "너무",
    "지금",
    "오늘",
    "우리",
    "저는",
    "제가",
    "그거",
    "이런",
    "저런",
    "그런",
    "것은",
    "것이",
    "것을",
    "것도",
    "수는",
    "수가",
    "있는",
    "없는",
    "합니다",
    "했습니다",
    "됩니다",
    "있습니다",
    "해당되는",
    "해당",
    "실제로",
    "마지막",
    "전체",
    "중심",
    "구간",
    "방식",
}

EN_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "that",
    "this",
    "these",
    "those",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "from",
    "by",
    "with",
    "about",
    "as",
    "into",
    "over",
    "under",
    "it",
    "its",
    "they",
    "them",
    "their",
    "we",
    "our",
    "you",
    "your",
    "i",
    "my",
    "he",
    "she",
    "his",
    "her",
    "will",
    "would",
    "can",
    "could",
    "should",
    "may",
    "might",
    "must",
    "do",
    "does",
    "did",
    "done",
    "have",
    "has",
    "had",
    "not",
    "no",
    "yes",
    "so",
    "very",
    "just",
    "also",
    "more",
    "most",
    "much",
    "many",
    "there",
    "here",
    "what",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "some",
    "each",
    "every",
    "other",
    "another",
    "thing",
    "things",
    "one",
    "two",
    "first",
    "second",
    "third",
}

EN_STOP_PHRASES = {
    "in the",
    "of the",
    "on the",
    "to the",
    "for the",
    "at the",
    "by the",
    "with the",
    "and the",
    "that the",
    "from the",
    "this is",
    "there is",
    "there are",
}

FILLER_WORDS = (
    "음",
    "어",
    "그",
    "인제",
    "이제",
    "그래서",
    "그다음",
    "그다음에",
)

NGRAM_WEIGHTS = {
    1: 1.0,
    2: 2.5,
    3: 3.0,
}

PARTICLE_PATTERN = re.compile(
    r"(은|는|이|가|을|를|에|의|와|과|도|로|으로|에서|에게|한테|께|"
    r"부터|까지|보다|처럼|마다|만|조차|마저|이나|나|라도|요|"
    r"라고|라는|이라고|이라는)$"
)

ENDING_FRAGMENT_PATTERN = re.compile(
    r"(그리고|그래서|그러면|그런데|하지만|때문에|같은|어떤|대한|대해|"
    r"으로|에서|에게|한테|부터|까지|라는|이라고|하고|거나|는데|"
    r"인데|고|며|지만)$"
)

COMPLETE_ENDING_PATTERN = re.compile(
    r"(다|요|됨|함|됨다|입니다|합니다|됩니다|했습니다|였다|었다|았다|"
    r"된다|한다|있다|없다|같다|된다라는|한다라는|[.!?。！？])$"
)

VERB_ENDING_PATTERN = re.compile(
    r"(하시면|하면|하고|했다|합니다|됩니다|되는|된다|한다|했고|해요|돼요|"
    r"나요|세요|이다|이며|면서|니까|는데|거나|라고|다고|같고|보고|듣고)$"
)

IMPORTANT_EXPRESSION_PATTERN = re.compile(
    r"(의미|중요|역할|차이|장점|단점|특징|구조|과정|원리|이유|결론|정리|"
    r"핵심|비교|관계|분류|관리|사용|통해|위해|때문|라고|란)"
)

EN_IMPORTANT_EXPRESSION_PATTERN = re.compile(
    r"\b(decided|maintain|reaffirmed|recognize|inflation|price stability|employment|"
    r"monetary policy|task force|review|framework|economic activity|unemployment|"
    r"federal funds rate)\b",
    re.IGNORECASE,
)

VAGUE_REFERENCE_PATTERN = re.compile(
    r"(^|\s)(그걸|이걸|저걸|그런|이런|저런|애들|뭐냐|왜 있냐면|같은 경우)(\s|은|는|이|가|을|를|$)"
)


def detect_language(text):
    hangul_count = len(re.findall(r"[가-힣]", text))
    english_count = len(re.findall(r"[A-Za-z]", text))
    total = hangul_count + english_count

    if total == 0:
        return "mixed"

    hangul_ratio = hangul_count / total
    english_ratio = english_count / total

    if hangul_ratio >= 0.55:
        return "ko"
    if english_ratio >= 0.55:
        return "en"
    return "mixed"


def read_transcript(input_path="outputs/transcript.txt"):
    try:
        with open(input_path, "r", encoding="utf-8") as input_stream:
            return input_stream.read()
    except FileNotFoundError:
        print(f"에러: 전사문 경로를 찾을 수 없습니다: {input_path}")
        return ""


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def normalize_word(word):
    word = PARTICLE_PATTERN.sub("", word)
    return word.strip()


def tokenize_sentence(sentence, language=None):
    language = language or detect_language(sentence)

    if language == "en":
        raw_tokens = re.findall(r"[A-Za-z]+", sentence.lower())
        return [
            token
            for token in raw_tokens
            if len(token) >= 3 and token not in EN_STOPWORDS and not token.isdigit()
        ]

    raw_tokens = re.split(r"[\s,.;:!?()\[\]{}\"'“”‘’\-_/]+", sentence.lower())
    tokens = []

    for token in raw_tokens:
        token = re.sub(r"^[^\w가-힣]+|[^\w가-힣]+$", "", token)
        token = normalize_word(token)

        if len(token) < 2:
            continue
        if token.isdigit():
            continue
        if token in STOPWORDS:
            continue
        if language == "mixed" and token in EN_STOPWORDS:
            continue
        if PARTICLE_PATTERN.fullmatch(token):
            continue
        if VERB_ENDING_PATTERN.search(token):
            continue
        tokens.append(token)

    return tokens


def tokenize_text(text, language=None):
    language = language or detect_language(text)
    tokens = []
    for sentence in split_sentences(text):
        tokens.extend(tokenize_sentence(sentence, language))
    return tokens


def clean_sentence(sentence, language=None):
    language = language or detect_language(sentence)
    sentence = sentence.strip()
    sentence = re.sub(r"\s+", " ", sentence)
    original_length = len(sentence)
    filler_count = 0

    if language != "en":
        for filler in FILLER_WORDS:
            sentence, count = re.subn(rf"(^|\s){re.escape(filler)}(\s|,|\.|$)", " ", sentence)
            filler_count += count

    sentence = re.sub(r"\s+", " ", sentence).strip(" ,.?!")
    if len(sentence) < 25:
        return ""
    if original_length and filler_count / max(len(sentence.split()), 1) > 0.18:
        return ""

    tokens = tokenize_sentence(sentence, language)
    if len(tokens) < 4:
        return ""

    token_counts = Counter(tokens)
    most_common_count = token_counts.most_common(1)[0][1]
    unique_ratio = len(token_counts) / len(tokens)

    if most_common_count / len(tokens) > 0.35:
        return ""
    if unique_ratio < 0.5:
        return ""
    if language == "en":
        if re.search(r"\b(and|or|but|because|with|for|from|into|about|that|which)$", sentence, re.IGNORECASE):
            return ""
    else:
        if ENDING_FRAGMENT_PATTERN.search(sentence):
            return ""
        if not COMPLETE_ENDING_PATTERN.search(sentence):
            return ""
        if VAGUE_REFERENCE_PATTERN.search(sentence) and not IMPORTANT_EXPRESSION_PATTERN.search(sentence):
            return ""

    if sentence_quality_score(sentence, tokens, language=language) < 0:
        return ""

    return sentence


def make_ngrams(tokens, n):
    return [" ".join(tokens[index : index + n]) for index in range(len(tokens) - n + 1)]


def is_contained_keyword(candidate, selected_keyword):
    candidate_tokens = candidate.split()
    selected_tokens = selected_keyword.split()

    if len(candidate_tokens) >= len(selected_tokens):
        return False

    for index in range(len(selected_tokens) - len(candidate_tokens) + 1):
        if selected_tokens[index : index + len(candidate_tokens)] == candidate_tokens:
            return True

    return False


def ngram_has_stopword(ngram, language):
    tokens = ngram.split()
    if language == "en":
        return any(token in EN_STOPWORDS for token in tokens) or ngram in EN_STOP_PHRASES
    if language == "mixed":
        return any(token in STOPWORDS or token in EN_STOPWORDS for token in tokens) or ngram in EN_STOP_PHRASES
    return any(token in STOPWORDS for token in tokens)


def extract_keywords(text, top_n=10):
    language = detect_language(text)
    ngram_counts = Counter()

    for sentence in split_sentences(text):
        tokens = tokenize_sentence(sentence, language)
        for n in NGRAM_WEIGHTS:
            for ngram in make_ngrams(tokens, n):
                if ngram_has_stopword(ngram, language):
                    continue
                ngram_counts[ngram] += 1

    scored_candidates = []
    for keyword, count in ngram_counts.items():
        tokens = keyword.split()
        n = len(tokens)
        if language != "en" and n > 1 and count < 2:
            continue

        if language == "en":
            english_weights = {
                1: 1.0,
                2: 3.0,
                3: 2.4,
            }
            score = count * english_weights[n]
            if n > 1:
                score += 2
        else:
            score = count * NGRAM_WEIGHTS[n]
        scored_candidates.append((score, n, count, keyword))

    scored_candidates.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3]))

    keywords = []
    for _, _, _, keyword in scored_candidates:
        if any(is_contained_keyword(keyword, selected) for selected in keywords):
            continue

        keywords = [
            selected
            for selected in keywords
            if not is_contained_keyword(selected, keyword)
        ]

        if len(keyword.split()) == 1 and any(keyword in selected.split() for selected in keywords):
            continue

        if keyword not in keywords:
            keywords.append(keyword)
        if len(keywords) >= top_n:
            break

    return keywords


def sentence_quality_score(sentence, sentence_words=None, keywords=None, language=None):
    language = language or detect_language(sentence)
    tokens = sentence_words or tokenize_sentence(sentence, language)
    if not tokens:
        return -20

    token_counts = Counter(tokens)
    token_count = len(tokens)
    unique_ratio = len(token_counts) / token_count
    repeated_ratio = token_counts.most_common(1)[0][1] / token_count
    numeric_token_ratio = sum(1 for token in tokens if re.search(r"\d", token)) / token_count
    hangul_chars = len(re.findall(r"[가-힣]", sentence))
    english_chars = len(re.findall(r"[A-Za-z]", sentence))
    visible_chars = len(re.findall(r"\S", sentence))
    hangul_ratio = hangul_chars / max(visible_chars, 1)
    english_ratio = english_chars / max(visible_chars, 1)
    filler_count = 0
    if language != "en":
        filler_count = sum(len(re.findall(rf"(^|\s){re.escape(filler)}(\s|$)", sentence)) for filler in FILLER_WORDS)
    stopword_source = EN_STOPWORDS if language == "en" else STOPWORDS
    if language == "mixed":
        stopword_source = STOPWORDS | EN_STOPWORDS
    raw_words = re.findall(r"[A-Za-z가-힣]+", sentence.lower())
    stopword_ratio = sum(1 for word in raw_words if word in stopword_source) / max(len(raw_words), 1)

    score = 0
    if token_count < 4:
        score -= 18
    elif token_count < 6:
        score -= 6
    elif 8 <= token_count <= 35:
        score += 8

    if len(sentence) < 25:
        score -= 18
    elif len(sentence) < 35:
        score -= 6
    elif 45 <= len(sentence) <= 160:
        score += 8
    elif len(sentence) > 220:
        score -= 16
    elif len(sentence) > 180:
        score -= 10

    if unique_ratio < 0.55:
        score -= 10
    else:
        score += unique_ratio * 8

    if repeated_ratio > 0.3:
        score -= 12
    if numeric_token_ratio > 0.1:
        score -= 10
    if language == "en" and english_ratio < 0.55:
        score -= 8
    elif language == "ko" and hangul_ratio < 0.7:
        score -= 8
    if stopword_ratio > 0.45:
        score -= 10
    if filler_count >= 2:
        score -= 6
    if language != "en" and VAGUE_REFERENCE_PATTERN.search(sentence):
        score -= 10
    if language != "en" and ENDING_FRAGMENT_PATTERN.search(sentence):
        score -= 14
    if language == "en" and not re.search(r"[.!?]$", sentence):
        score -= 4
    elif language != "en" and not re.search(r"[.!?。！？다요음임]$", sentence):
        score -= 6
    if language == "en" and EN_IMPORTANT_EXPRESSION_PATTERN.search(sentence):
        score += 10
    elif language != "en" and IMPORTANT_EXPRESSION_PATTERN.search(sentence):
        score += 8

    if keywords:
        token_set = set(tokens)
        for keyword in keywords:
            keyword_tokens = keyword.split()
            if len(keyword_tokens) == 1 and keyword in token_set:
                score += 2
            elif len(keyword_tokens) > 1 and all(token in token_set for token in keyword_tokens):
                score += 4 + len(keyword_tokens)

    return score


def is_similar_sentence(sentence, selected_sentences, language=None):
    language = language or detect_language(sentence)
    sentence_words = set(tokenize_sentence(sentence, language))
    if not sentence_words:
        return True

    for selected_sentence in selected_sentences:
        selected_words = set(tokenize_sentence(selected_sentence, language))
        if not selected_words:
            continue

        overlap = sentence_words & selected_words
        similarity = len(overlap) / max(len(sentence_words), len(selected_words))
        if similarity >= 0.55:
            return True

    return False


def polish_summary_sentence(sentence, language=None):
    language = language or detect_language(sentence)
    sentence = clean_sentence(sentence, language)
    if not sentence:
        return ""

    sentence = re.sub(r"\s+", " ", sentence).strip(" ,.")
    if len(sentence) > 160:
        sentence = sentence[:160].rsplit(" ", 1)[0].strip(" ,.")
        if len(sentence) < 40:
            return ""
        if language != "en" and ENDING_FRAGMENT_PATTERN.search(sentence):
            return ""
        if language == "en" and re.search(r"\b(and|or|but|because|with|for|from|into|about|that|which)$", sentence, re.IGNORECASE):
            return ""

    if sentence.endswith(("...", ".", "!", "?")):
        return f"- {sentence}"

    if language == "en":
        return f"- {sentence}."

    if sentence.endswith(("다", "요", "음", "임")):
        return f"- {sentence}."

    return f"- {sentence}."


def summarize_text(text, max_sentences=5):
    # 외부 LLM 없이 규칙 기반으로 전사문에서 핵심 문장을 추출하는 방식이다.
    language = detect_language(text)
    candidates = []
    keyword_list = extract_keywords(text, top_n=20)
    keyword_set = set(keyword_list)

    for index, sentence in enumerate(split_sentences(text)):
        cleaned_sentence = clean_sentence(sentence, language)
        if not cleaned_sentence:
            continue

        tokens = tokenize_sentence(cleaned_sentence, language)
        token_set = set(tokens)
        score = sentence_quality_score(cleaned_sentence, tokens, keyword_list, language)
        if score < 18:
            continue

        score += sum(1 for token in token_set if token in keyword_set)
        candidates.append((score, index, cleaned_sentence))

    selected_sentences = []
    for _, index, sentence in sorted(candidates, key=lambda item: item[0], reverse=True):
        if is_similar_sentence(sentence, [item[1] for item in selected_sentences], language):
            continue

        selected_sentences.append((index, sentence))
        if len(selected_sentences) >= max_sentences:
            break

    selected_sentences.sort(key=lambda item: item[0])

    bullets = []
    seen_bullets = set()
    for _, sentence in selected_sentences:
        bullet = polish_summary_sentence(sentence, language)
        if bullet and bullet not in seen_bullets:
            bullets.append(bullet)
            seen_bullets.add(bullet)

    return "\n".join(bullets)


def save_summary(summary, keywords, output_path="outputs/summary.txt"):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_stream:
        output_stream.write("[요약]\n")
        output_stream.write(summary)
        output_stream.write("\n\n[핵심 키워드]\n")
        output_stream.write(", ".join(keywords))

    return output_path


if __name__ == "__main__":
    transcript = read_transcript()
    if transcript:
        summary_text = summarize_text(transcript)
        keyword_list = extract_keywords(transcript)
        saved_path = save_summary(summary_text, keyword_list)
        print("요약 완료")
        print(f"요약 저장 완료: {saved_path}")
