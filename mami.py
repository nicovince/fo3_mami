#!/usr/bin/env python
# Solve Mastermind kind of game present in Fallout 3

class Session:
    def __init__(self):
        # Dictionnary of password/number of good positions
        self.passwords = {}

    def add_password(self, passwd):
        """Add a password to the list, initialize number of good positions to None"""
        if not self.passwords.has_key(passwd):
            self.passwords[passwd] = None
        else:
            print "password %s already present in list" % passwd

    def delete_password(self, passwd):
        """Remove a password from the list"""
        self.passwords.pop(password, None)

    def try_password(self, passwd, n):
        """Reccord n as number of good positions for password"""
        if self.passwords.has_key(passwd):
            if self.passwords[passwd] != n and self.passwords[passwd] is not None:
                print "Password %s already, number of good positions was %d, now set to %d" % (passwd, self.passwords[passwd], n)
        self.passwords[passwd] = n

    def find_common(self, passwd, n):
        """Return list of password who share n letters in common with given password"""
        return


if __name__ == "__main__":
    print "hello world"
    session = Session()
    session.add_password("foo")
    session.add_password("bar")
    session.add_password("for")

