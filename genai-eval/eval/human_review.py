def human_review_needed(output, expected, similarity, threshold=0.6):
    """
    Flag samples that need human review.
    Example: low semantic similarity or uncertain correctness.
    """
    if similarity < threshold:
        return True
    return False
