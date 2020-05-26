import os
import os.path
import sys
import argparse
import django
dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
from loginSys.models import Account
from loginSys.forms import checkPassword, checkEmail, checkUsername
from plogical.hashPassword import hash_password


def main(argv):
    try:
        mode = argv.mode
        account = Account.objects.filter().first()
        if mode == 'create':
            if account is not None:
                raise ValueError('Account has been existed!')
            username = argv.username
            password = argv.password
            email = argv.email
            firstname = argv.firstname
            lastname = argv.lastname
            # validate
            checkUsername(username)
            checkEmail(email)
            checkPassword(password)
            account = Account(login_id=username, password=hash_password(password), email=email, first_name=firstname, last_name=lastname)
            account.save()
            print('Create User successfully!\nDone!')
        else:
            password = argv.password
            if account is None:
                print('No accounts have been created yet!')
            else:
                checkPassword(password)
                account = Account.objects.get(pk=account.id)
                account.password = hash_password(password)
                account.save()
                print('Change password successfully!\nDone!')
    except BaseException as e:
        print('Error: {}'.format(str(e)))


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', type=str, choices=['create', 'reset'], help='Indicates if a new user or change user!', default='create')
    return parser.parse_known_args(argv)


def create_parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', type=str, choices=['create', 'reset'], help='Indicates if a new user or change user!', default='create')

    parser.add_argument('-u', '--username', type=str, help='Name user login cPanel.', required=True)
    parser.add_argument('-p', '--password', type=str, help='Password login cPanel.', required=True)
    parser.add_argument('-e', '--email', type=str, help='Email manager cPanel.', default='kythuat@runsystem.net')
    parser.add_argument('-fn', '--firstname', type=str, help='First Name User.', default='Secure')
    parser.add_argument('-ln', '--lastname', type=str, help='Last name User.', default='Vps')

    return parser.parse_args(argv)


def change_parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', type=str, choices=['create', 'reset'], help='Indicates if a new user or change user!',
                        default='create')
    parser.add_argument('-p', '--password', type=str, help='Password login cPanel.', required=True)

    return parser.parse_args(argv)


if __name__ == '__main__':

    argsBase = parse_arguments(sys.argv[1:])
    if argsBase[0].mode == 'create':
        main(create_parse_arguments(sys.argv[1:]))
    else:
        main(change_parse_arguments(sys.argv[1:]))

