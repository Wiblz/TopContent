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


def format_number(number):
    return f'{"🔺" if number > 0 else "🔻"}{abs(number):.2f}'
