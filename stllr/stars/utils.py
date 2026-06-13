def calculate_brightness(total_stars, user_count):
    d = user_count - total_stars
    if d == 0:
        return 1e15
    if d == user_count:
        return 1e-15
    return 1 / (d ** 2)
