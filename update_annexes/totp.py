import pyotp
import argparse

args = None
def parse() -> None:

        global args

        parser = argparse.ArgumentParser(
        prog="totp.py",
        description="Tool to obtain the totp value",
        epilog="",
	)
        
        parser.add_argument(
        "--totp_key",
        action="store",
        dest="totp_key",
        help="Value of totp's key",
        required=True,
    	)
    
        args = parser.parse_args()
    
def main() -> None:

	parse()
	
	totp = pyotp.TOTP(args.totp_key)

	print(totp.now())
	
if __name__ == "__main__":
    main()
