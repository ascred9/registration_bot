import environs
import github


class GitApi:
    env = environs.Env()
    env.read_env('data/.env')
    g = github.Github(env('GIT_TOKEN'))
    org_name = "NSU-Programming"
    org = g.get_organization(org_name)

    @classmethod
    def invite(cls, mail: str):
        for org in cls.g.get_user().get_orgs():
            if org.login == cls.org.login:
                org.invite_user(email=mail)
                break

    @classmethod
    def remove_user(cls, mail: str):
        for org in cls.g.get_user().get_orgs():
            if org.login == cls.org.login:
                for user in cls.org.invitations():
                    print(user.email)
                    if mail == user.email:
                        # cls.org.cancel_invitation("sansopanso")
                        break
                break

# print(type(g.get_user("sansopanso")))
# print(g.get_organization("NSU-Programming"))
# for org in g.get_user().get_orgs():
#    print(org.login)
# for user in org.get_members():
#    print(user)
