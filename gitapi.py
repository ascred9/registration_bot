import environs
import time
import github


class GitApi:
    env = environs.Env()
    env.read_env('data/.env')
    g = github.Github(env('GIT_TOKEN'))
    org_name = "NSU-Programming"
    org = g.get_organization(org_name)
    team_name = "Students"
    teams = [org.get_team_by_slug(team_name)]

    @classmethod
    def invite(cls, mail: str):
        cls.org.invite_user(email=mail, teams=cls.teams)

    @classmethod
    def is_user_pending(cls, mail: str):
        for user in cls.org.invitations():
            if mail == user.email:
                #cls.org.cancel_invitation(mail)
                return True
        return False


    @classmethod
    def convert_student_to_outside_collaborator(cls, username: str):
        cls.org.convert_to_outside_collaborator(cls.g.get_user(username))

    @classmethod
    def update_invitations(cls, sleep_time):
        while True:
            for user in cls.teams[0].get_members():
                cls.convert_student_to_outside_collaborator(user.login)
            time.sleep(sleep_time)
