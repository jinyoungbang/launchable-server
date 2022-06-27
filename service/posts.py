import datetime


def find_and_push_comment(comments, parents, data):
    if len(parents) == 1:
        for comment in comments:
            if comment["id"] == parents[0]:
                comment["comments"].append(data)
                comment["comments_count"] += 1
                return

    for comment in comments:
        if comment["id"] == parents[0]:
            find_and_push_comment(comment["comments"], parents[1:], data)

    return


def find_and_update_comment(comments, comment_id, parents, body):
    if len(parents) == 0:
        for comment in comments:
            if comment["id"] == comment_id:
                comment["body"] = body
                comment["updated_at"] = datetime.datetime.now()
                return

    else:
        for comment in comments:
            if comment["id"] == parents[0]:
                find_and_update_comment(
                    comment["comments"], comment_id, parents[1:], body)

    return


def find_and_delete_comment(comments, comment_id, parents):
    if len(parents) == 0:
        for comment in comments:
            if comment["id"] == comment_id:
                comment["deleted"] = True
                comment["updated_at"] = datetime.datetime.now()
                return


    else:
        for comment in comments:
            if comment["id"] == parents[0]:
                find_and_delete_comment(comment["comments"], comment_id, parents[1:])

