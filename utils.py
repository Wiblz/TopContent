def get_max_formatted_number_length(posts, attr):
    try:
        return max([len(format(getattr(post, attr), '+.2f')) for post in posts])
    except ValueError:
        print(f'No attribute {attr} in posts.')
        return 0


def get_max_str_length(posts, attr):
    try:
        return max([len(str(getattr(post, attr))) for post in posts])
    except ValueError:
        print(f'No attribute {attr} in posts.')
        return 0


def set_differences(community, post_list):
    for post in post_list:
        post.set_difference(community)


def format_number(number, inverse=False, small=False):
    number = -number if inverse else number
    prefix = "🔺" if number > 0 else "🔻"
    a = abs(number)
    if small:
        return f'{prefix} {number:+.2f}'
    else:
        if a < 1000:
            # convert to integer and keep the sign
            return f'{prefix} {"+" if number > 0 else "-"}{round(a)}'
        elif a < 100000:
            # round to a number of thousands
            return f'{prefix} {"+" if number > 0 else "-"}{round(a / 1000, 1)}k'
        elif a < 1000000:
            # round to a whole number of thousands
            return f'{prefix} {"+" if number > 0 else "-"}{round(a / 1000)}k'
        elif a < 100000000:
            # round to a number of millions
            return f'{prefix} {"+" if number > 0 else "-"}{round(a / 1000000, 1)}m'
        else:
            # round to a whole number of millions
            return f'{prefix} {"+" if number > 0 else "-"}{round(a / 1000000)}m'
