#!/usr/bin/python
import sys
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import Paper, UserProfile, GroupProfile

def generate_filename(output_dir, p):
    # Replace spaces with underscores and remove special characters
    sanitized_title = re.sub(r'\W+', '_', p.title.replace(' ', '_'))

    # Replace multiple underscores with a single one
    sanitized_title = re.sub('_+', '_', sanitized_title)

    # Trim to at most 50 characters without splitting words
    words = sanitized_title.split('_')
    trimmed_title = ''
    for word in words:
        if len(trimmed_title) + len(word) + 1 > 50:  # +1 for the underscore
            break
        trimmed_title += (word + '_')
    trimmed_title = trimmed_title.rstrip('_')  # Remove trailing underscore

    filename = os.path.join(output_dir, p.create_time.strftime('%Y%m%d') + '_' + trimmed_title + '.md')
    return filename

def main():
    if len(sys.argv) < 2:
        print("Usage: export-by-user.py <user_id_or_nickname> [output_dir]")
        sys.exit(1)

    user_id_or_nickname = sys.argv[1]

    if user_id_or_nickname.isdigit():
        # Argument is an integer, so we try filtering by primary key (pk)
        u = UserProfile.objects.filter(pk=int(user_id_or_nickname))
    else:
        # Argument is not an integer, so we proceed with filtering by nickname
        u = UserProfile.objects.filter(nickname=user_id_or_nickname)

    # Proceed with your logic here
    # Note: 'u' will be a QuerySet, which can contain zero, one, or more items.
    # You might want to handle these cases accordingly, for example:
    if not u.exists():
        print("No user found.")
        return

    g = GroupProfile.objects.get(name='xiangma')

    output_dir = ''
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

    papers = g.papers.filter(creator__in=u)
    print('Total papers: ', papers.count())
    for p in papers:
        if not output_dir:
            print('=========================================')
            print('Create Time: ', p.create_time.strftime('%Y-%m-%d %H:%M:%S'))
            print('Update Time: ', p.update_time.strftime('%Y-%m-%d %H:%M:%S'))
            print('Title: ', p.title)
            print('Journal: ', p.journal)
            print('Year: ', p.pub_year)
            print('Creator: ', p.creator.nickname)
            print('Comment: ', p.comments)
            print()
        else:
            filename = generate_filename(output_dir, p)
            with open(filename, 'w') as f:
                f.write(f'# {p.pub_year}, {p.journal}, {p.title}\n')
                f.write('\n')
                f.write(p.create_time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
                f.write('\n')
                f.write(f'{p.comments}\n')

    return 0

if __name__ == "__main__":
    main()
