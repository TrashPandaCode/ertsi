from treble_tsdk import display_data as dd
from treble_tsdk.tsdk import TSDK, TSDKCredentials, 

def main():
    tsdk = TSDK(TSDKCredentials.from_file("./creds/tsdk.cred"))


if __name__ == "__main__":
    main()
