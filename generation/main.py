from treble_tsdk.tsdk import TSDK, TSDKCredentials
from treble_tsdk import display_data as dd
from treble_tsdk import treble

def main():
    tsdk = TSDK(TSDKCredentials.from_file("./creds/tsdk.cred"))

    projects = tsdk.list_my_projects()
    dd.display(projects)

    project = tsdk.get_or_create_project("ertsi")


if __name__ == "__main__":
    main()
