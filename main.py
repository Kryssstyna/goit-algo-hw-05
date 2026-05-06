from pathlib import Path
import timeit
from collections import defaultdict


def read_text(filename):
    path = Path(filename)

    for encoding in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="utf-8", errors="ignore")


def boyer_moore_search(text, pattern):
    n = len(text)
    m = len(pattern)

    if m == 0:
        return 0

    bad_char = {}

    for i in range(m):
        bad_char[pattern[i]] = i

    shift = 0

    while shift <= n - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1

        if j < 0:
            return shift

        bad_char_shift = j - bad_char.get(text[shift + j], -1)
        shift += max(1, bad_char_shift)

    return -1


def build_prefix_table(pattern):
    prefix = [0] * len(pattern)
    j = 0

    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = prefix[j - 1]

        if pattern[i] == pattern[j]:
            j += 1
            prefix[i] = j

    return prefix


def kmp_search(text, pattern):
    if pattern == "":
        return 0

    prefix = build_prefix_table(pattern)
    j = 0

    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = prefix[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == len(pattern):
            return i - j + 1

    return -1


def rabin_karp_search(text, pattern):
    n = len(text)
    m = len(pattern)

    if m == 0:
        return 0

    if m > n:
        return -1

    base = 256
    prime = 101

    pattern_hash = 0
    text_hash = 0
    h = 1

    for _ in range(m - 1):
        h = (h * base) % prime

    for i in range(m):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % prime
        text_hash = (base * text_hash + ord(text[i])) % prime

    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i + m] == pattern:
                return i

        if i < n - m:
            text_hash = (
                base * (text_hash - ord(text[i]) * h)
                + ord(text[i + m])
            ) % prime

            if text_hash < 0:
                text_hash += prime

    return -1


def choose_existing_substring(text, candidates):
    for substring in candidates:
        if substring in text:
            return substring

    start = len(text) // 3
    return text[start:start + 25]


def choose_fake_substring(text):
    fake = "квантовий алгоритм сортування"

    while fake in text:
        fake += " xyz"

    return fake


def measure_time(function, text, pattern, number=100, repeat=5):
    timer = timeit.Timer(lambda: function(text, pattern))
    result = timer.repeat(repeat=repeat, number=number)

    return min(result) / number * 1000


def main():
    articles = {
        "Стаття 1": read_text("стаття 1.txt"),
        "Стаття 2": read_text("стаття 2 (1).txt"),
    }

    existing_candidates = {
        "Стаття 1": [
            "двійковий пошук",
            "Алгоритми пошуку",
            "жадібний алгоритм",
        ],
        "Стаття 2": [
            "рекомендаційної системи",
            "структури даних",
            "хеш-таблиця",
        ],
    }

    algorithms = {
        "Боєра-Мура": boyer_moore_search,
        "Кнута-Морріса-Пратта": kmp_search,
        "Рабіна-Карпа": rabin_karp_search,
    }

    results = []

    for article_name, text in articles.items():
        existing_substring = choose_existing_substring(
            text,
            existing_candidates[article_name]
        )

        fake_substring = choose_fake_substring(text)

        patterns = {
            "існуючий": existing_substring,
            "вигаданий": fake_substring,
        }

        for pattern_type, pattern in patterns.items():
            for algorithm_name, algorithm_function in algorithms.items():
                index = algorithm_function(text, pattern)

                elapsed_time = measure_time(
                    algorithm_function,
                    text,
                    pattern
                )

                results.append({
                    "article": article_name,
                    "pattern_type": pattern_type,
                    "pattern": pattern,
                    "algorithm": algorithm_name,
                    "time": elapsed_time,
                    "index": index,
                })

    print("\nРЕЗУЛЬТАТИ ВИМІРЮВАННЯ\n")

    print("| Текст | Тип підрядка | Підрядок | Алгоритм | Індекс | Час, мс |")
    print("|---|---|---|---|---:|---:|")

    for row in results:
        print(
            f"| {row['article']} "
            f"| {row['pattern_type']} "
            f"| {row['pattern']} "
            f"| {row['algorithm']} "
            f"| {row['index']} "
            f"| {row['time']:.6f} |"
        )

    grouped_by_article = defaultdict(list)

    for row in results:
        grouped_by_article[row["article"]].append(row)

    print("\nНАЙШВИДШИЙ АЛГОРИТМ ДЛЯ КОЖНОГО ТЕКСТУ\n")

    for article_name, rows in grouped_by_article.items():
        algorithm_times = defaultdict(list)

        for row in rows:
            algorithm_times[row["algorithm"]].append(row["time"])

        averages = {
            algorithm: sum(times) / len(times)
            for algorithm, times in algorithm_times.items()
        }

        best_algorithm = min(averages, key=averages.get)

        print(
            f"{article_name}: найшвидший алгоритм — {best_algorithm}, "
            f"середній час: {averages[best_algorithm]:.6f} мс"
        )

    overall_times = defaultdict(list)

    for row in results:
        overall_times[row["algorithm"]].append(row["time"])

    overall_averages = {
        algorithm: sum(times) / len(times)
        for algorithm, times in overall_times.items()
    }

    best_overall = min(overall_averages, key=overall_averages.get)

    print("\nЗАГАЛЬНИЙ ВИСНОВОК\n")

    for algorithm, avg_time in overall_averages.items():
        print(f"{algorithm}: середній час {avg_time:.6f} мс")

    print(
        f"\nНайшвидший алгоритм загалом — {best_overall}, "
        f"середній час: {overall_averages[best_overall]:.6f} мс"
    )


if __name__ == "__main__":
    main()