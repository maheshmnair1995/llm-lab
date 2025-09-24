from transformers import pipeline
import re

# Use a smaller, robust summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def clean_text(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<.*?>", " ", text)  # remove HTML tags
    text = re.sub(r"\s+", " ", text)    # collapse multiple spaces/newlines
    return text.strip()

def extract_keywords(text: str, max_keywords=3) -> str:
    """Simple keyword extraction: pick top unique words from title/content."""
    words = [w.strip('.,').capitalize() for w in text.split()]
    seen = set()
    keywords = []
    for w in words:
        if w.lower() not in seen:
            seen.add(w.lower())
            keywords.append(w)
        if len(keywords) >= max_keywords:
            break
    return ", ".join(keywords)

def summarize_text(title: str, content: str, max_tokens: int = 200) -> str:
    title = clean_text(title)
    content = clean_text(content)

    if not title and not content:
        return "No content to summarize."

    text = f"{title}. {content}".strip()

    # Handle very short text
    if len(text.split()) < 10:
        keywords = extract_keywords(title)
        return f"{text}\nKeywords: {keywords}"

    # Truncate very long text for the model (max ~1024 tokens)
    max_words = 800
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])

    try:
        summary_list = summarizer(
            text,
            max_length=min(max_tokens, len(text.split()) * 2),
            min_length=min(30, len(text.split())),
            do_sample=False
        )

        summary = summary_list[0]['summary_text'].strip()
        keywords = extract_keywords(title)

        return f"{summary}\nKeywords: {keywords}"

    except Exception as e:
        # Fallback
        keywords = extract_keywords(title)
        return f"{text}\nKeywords: {keywords}\n(Note: summarization failed: {e})"


# Example usage
if __name__ == "__main__":
    title = "Arab Spring activist Alaa Abdel Fattah released after pardon from Egypt’s Sisi"
    content = """
    <ol><li><a href="https://news.google.com/rss/articles/CBMihgFBVV95cUxOMnhxWGhDVnZtRXZYUlBJZF9oMFk0WjkxRHVoQmRpVXVNenpwVm1QWUVBRFY2NjFLalpvMUNhdS1Ud3FSYjBLbkhTS2R4bE9rYVJwcEhtRHgxeWxfcUxCanA2czhtNWRmZ1hQYndvRGVzTXFDM2JYSVJOeGliNC04YlJXd2pjQQ?oc=5" target="_blank">Arab Spring activist Alaa Abdel Fattah released after pardon from Egypt’s Sisi</a></li></ol>
    """
    print(summarize_text(title, content))
