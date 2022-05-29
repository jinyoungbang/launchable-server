
class Post(object):
    def __init__(self, id, title, body, user, created_at, updated_at):
        self.id = id
        self.title = title
        self.body = body
        self.user = user
        self.likes = []
        self.likes_count = 0
        self.views = 0
        self.created_at = created_at
        self.updated_at = updated_at
        self.comments = []
        self.comments_count = 0
        self.liked = False


class Comment(object):
    def __init__(self, id, body, user_id, username, level, created_at, updated_at):
        self.id = id
        self.body = body
        self.user_id = user_id
        self.username = username
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at
        self.likes = 0
        self.comments = []
        self.comments_count = 0
        self.deleted = False


class Like(object):
    def __init__(self, user_id: str, post_id: str, created_at):
        self.user_id = user_id
        self.post_id = post_id
        self.created_at = created_at

#   type Comment {
#     id: ID!
#     text: String
#     likes: Int
#     level: Int
#     has_replies: Boolean
#     deleted: Boolean
#     user: User
#     replies: [Comment]
#     created_at: Date
#     replies_count: Int
#   }
