#!/usr/bin/env python
# Solve Mastermind kind of game present in Fallout 3

import sys

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

    def ui_add_password(self):
        """User interface for adding password to the list"""
        password = raw_input("Add password to the list : ").upper()
        # check length of password
        if len(self.passwords) != 0:
            password_len = len(self.passwords.keys()[0])
            while len(password) != password_len:
                print "Wrong password length, expecting %d character" % password_len
                password = raw_input("Add password to the list : ").upper()

        self.add_password(password)

    def ui_try_password(self):
        """User interface to test password"""
        idx = 1
        # List passwords with number of good letters when available
        for p in self.passwords.keys():
            if self.passwords[p] != None:
                print "%d) %s : %d good letters" % (idx, p, self.passwords[p])
            else:
                print "%d) %s" % (idx, p)
            idx = idx + 1
        # Get user input and check it
        choice = raw_input("Which password do you want to try : ")
        while not self.check_numerical_choice(choice, 1, len(self.passwords)):
            print "Invalid choice, must be in range %d - %d" % (1, len(self.passwords))
            choice = raw_input("Which password do you want to try : ")
        choice = int(choice)

        # Get number of good letters for tried password
        password = self.passwords.keys()[choice - 1]
        nb_good_letters = raw_input("How many good letters in %s : " % (password))
        while not self.check_numerical_choice(nb_good_letters, 0, len(password)):
            nb_good_letters = raw_input("How many good letters in %s : " % (password))
        nb_good_letters = int(nb_good_letters)

        # Record number of letters for the tested password
        self.try_password(password, nb_good_letters)

    def ui_find_candidates(self):
        """Display remaining candidates"""
        print "Remaining candidates are " + str(self.get_candidates())

    def menu(self):
        """Display main menu and ask for user choice"""
        # key : [ text, function to execute]
        menu_map = {"a" : ["(a)dd password", self.ui_add_password],
                    "t" : ["(t)ry password", self.ui_try_password],
                    "f" : ["(f)ind candidates", self.ui_find_candidates],
                    "q" : ["(q)uit", sys.exit]}
        while True:
            # Display menu
            for k in menu_map.keys():
                print menu_map[k][0]
            # Read choice from user and check it
            choice = raw_input("Choice : ")
            while not self.check_alpha_choice(choice, menu_map.keys()):
                print "Invalid choice : %s" % choice
                choice = raw_input("Choice : ")
            # Execute selected choice
            menu_map[choice][1]()
            print ""

    @classmethod
    def check_numerical_choice(cls, n , lower, upper):
        """Check choice is in integer range"""
        if n.isdigit():
            return int(n) in range(lower, upper + 1)
        else:
            return False

    @classmethod
    def check_alpha_choice(cls, c, choices):
        """Check choice is in list of choices"""
        return c in choices


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

def test_autoplay():
    session = Session()
    for p in passwords:
        session.add_password(p)
    session.autoplay("FRIES")

def test_play():
    session = Session()
    session.ui_add_password()
    session.ui_add_password()
    session.ui_try_password()
    print session.get_candidates()

if __name__ == "__main__":
    test_autoplay()
    session = Session()
    session.menu()


