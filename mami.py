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
        """
        Reccord n as number of good positions for password
        
        Return True if n is equals to length of passwd
        """
        if self.passwords.has_key(passwd):
            if self.passwords[passwd] != n and self.passwords[passwd] is not None:
                print "Password %s already, number of good positions was %d, now set to %d" % (passwd, self.passwords[passwd], n)
        self.passwords[passwd] = n
        return len(passwd) == n

    @classmethod
    def get_nb_common(cls, p1, p2):
        """Return number of letters at same positions in p1 and p2"""
        assert(len(p1) == len(p2))
        nb_commons = 0
        for idx in range(len(p1)):
            if p1[idx] == p2[idx]:
                nb_commons = nb_commons + 1
        return nb_commons


    def find_common(self, passwd, n):
        """Return list of password who share n letters in common with given password"""
        commons = []
        for p in self.passwords:
            if p != passwd:
                nb_commons = self.get_nb_common(passwd, p)
                if nb_commons == n:
                    commons.append(p)
        return commons

    def get_candidates(self):
        """Based on state of list of passwords and number of good letters, return list of candidates"""
        # Initialize candidates with passwords not tested yet
        candidates = [c for c in self.passwords.keys() if self.passwords[c] == None]
        tried_passwords = [p for p in self.passwords.keys() if self.passwords[p] != None]
        for p in tried_passwords:
            if len(p) == self.passwords[p]:
                candidates = [p]
                break;
            sub_candidates = self.find_common(p, self.passwords[p])
            candidates = [c for c in candidates if c in sub_candidates]
        return candidates

    def autoplay(self, match):
        """Autoplay current session with provided password"""
        candidates = self.get_candidates()
        while len(candidates) != 1:
            trial = candidates[0]
            print "Test %s from "  % (trial) + str(candidates)
            if self.try_password(trial, self.get_nb_common(trial, match)):
                candidates = [trial]
            else:
                candidates = self.get_candidates()
        print candidates[0]

    def clear_trials(self):
        """Clear trials on list of passwords"""
        for k in self.passwords.keys():
            self.passwords[k] = None

# Example of password list
passwords = ["DRIED",
             "FREED",
             "GREED",
             "CARED",
             "TRULY",
             "TIRED",
             "CRIED",
             "TRAIL",
             "THIRD",
             "TRUTH",
             "CREED",
             "FLUID",
             "FRIES"]

if __name__ == "__main__":
    print "hello world"
    session = Session()
    session.add_password("foo")
    session.add_password("bar")
    session.add_password("for")
    print "candidates are " + str(session.get_candidates())
    session.try_password("foo", 2)
    print session.find_common("foo", 2)
    print "candidates are " + str(session.get_candidates())
    print "------------"
    session = Session()
    for p in passwords:
        session.add_password(p)
    session.autoplay("FRIES")
    session.clear_trials()
    session.autoplay("CREED")


