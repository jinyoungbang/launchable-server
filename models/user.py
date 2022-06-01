class User(object):
    def __init__(self, id, username, email, created_at, updated_at, is_valid):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_valid = is_valid
        self.profile = vars(UserProfile(id, "", created_at, updated_at, "", {}))

    def __repr__(self):
        return(
            f'User(\
                id={self.id}, \
                username={self.username}, \
                email={self.email}, \
                created_at={self.created_at}, \
                updated_at={self.updated_at}, \
                is_valid={self.is_valid}, \
                profile={self.profile}, \
            )'
        )

class UserProfile(object):
    def __init__(self, id, display_name, created_at, updated_at, about, profile_links):
        self.id = id
        self.display_name = display_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.about = about
        self.profile_links = profile_links


    def __repr__(self):
        return(
            f'UserProfile(\
                id={self.id}, \
                display_name={self.display_name}, \
                created_at={self.created_at}, \
                updated_at={self.updated_at}, \
                about={self.about}, \
                profile_links={self.profile_links}, \
            )'
        )
