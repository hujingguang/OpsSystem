from modles import Account

class MyAuth:
    def authenticate(self, username=None, password=None):
	try:
	    user = Account.object.get(username=username)
	except Account.DoesNotExist:
	    pass
	else:
	    if user.check_password(password):
		return user
	return None
    def get_user(self, user_id):
	try:
	    return Account.object.get(pk=user_id)
	except Account.DoesNotExist:
	    return None



