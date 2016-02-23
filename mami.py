#!/usr/bin/env python
# Solve Mastermind kind of game present in Fallout 3

import sys
import curses
import curses.textpad
import time

class Session:
    def __init__(self):
        # Dictionnary of password/number of good positions
        self.passwords = {}
        self.password_len = 0

    def add_password(self, passwd):
        """Add a password to the list, initialize number of good positions to None"""
        if not self.passwords.has_key(passwd):
            self.passwords[passwd] = None
            self.password_len = len(passwd)
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

class Pipboy(object):
    """Curses interface for solving master mind game"""
    def __init__(self):
        self.session = Session()
        self.setup_menu()
        # Global window
        self.stdscr = curses.initscr()
        # To be able to do getch()
        self.stdscr.keypad(1)
        # Size of global window
        self.y, self.x = self.stdscr.getmaxyx()
        # Do not echo input
        curses.noecho()
        # Get key pressed immediately
        curses.cbreak()
        # User window, with border and prompt [Bottom]
        self.usr_win = curses.newwin(2, self.x, self.y - 3, 0)
        self.usr_win.addstr(0, 0, "-" * self.x)
        self.usr_win.addstr(1, 2, "> ")
        # Text window where user enters commands
        self.text_box_win = curses.newwin(1, self.x, self.y - 2, 4)
        # Text box where user commands are read from
        self.text_box = curses.textpad.Textbox(self.text_box_win)
        # Debug window [ First line]
        self.dbg_win = curses.newwin(1, self.x, 0, 0)
        # Menu window, above user window
        self.menu_win = curses.newwin(2, self.x, self.y - 5, 0)
        # items windows, where password are displayed
        y,x = self.menu_win.getbegyx()
        self.dbg_print("y : %d - x : %d" % (y, x))
        self.item_win = curses.newwin(y-1, 0, 0, 0)


    def dbg_print(self, s):
        """Print string in debug window"""
        self.dbg_win.clear()
        self.dbg_win.addstr(0, 0, s)
        self.dbg_win.refresh()

    @classmethod
    def exit(cls):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def setup_menu(self):
        self.menu = [{"a" : {"text" : "(a)dd password",
                             "callback" : self.add_password}},
                     {"t" : {"text" : "(t)ry password",
                             "callback" : None}},
                     {"f" : {"text" : "(f)ind candidates",
                             "callback" : None}},
                     {"q" : {"text" : "(q)uit",
                             "callback" : sys.exit}}]


    def get_menu_callback(self, key):
        """Get callback for given menu key"""
        for entry in self.menu:
            if entry.keys()[0] == key:
                return entry[key]["callback"]
        return None

    def display_options(self, options):
        """Display options in menu window"""
        self.menu_win.clear()
        self.menu_win.move(0, 2)
        for opt in options:
            self.menu_win.addstr(opt + "   ")
        self.menu_win.refresh()

    def display_menu(self):
        menulist = []
        for entry in self.menu:
            key = entry.keys()[0]
            menulist.append(entry[key]["text"])
        self.display_options(menulist)

    def clear_menu(self):
        self.menu_win.clear()
        self.menu_win.refresh()

    def add_password(self):
        """Adds password to current session"""
        if len(self.session.passwords) > 0:
            self.display_items(self.session.passwords)
        self.usr_win.refresh()
        self.display_options(["Enter password candidate"])
        password = self.text_box.edit()
        self.session.add_password(password)
        self.text_box_win.clear()
        self.text_box_win.refresh()
        self.display_items(self.session.passwords)
        self.clear_menu()

    def main_loop(self):
        """Adds/Try password or quit"""
        self.display_menu()
        while True:
            self.usr_win.refresh()
            key = self.text_box_win.getkey()
            callback = self.get_menu_callback(key.strip())
            if callback != None:
                callback()
                self.display_menu()


    def display_passwords(self, hl_password=""):
        """Display list of passwords with number of good letters

        Highlight the provided password if available
        """
        self.item_win.clear()
        if len(self.session.passwords) == 0:
            center = self.x / 2
            msg = "No password"
            self.item_win.addstr(10, center - len(msg)/2, msg)
            self.item_win.refresh()
        else:
            line_offset = 3
            idx = 0
            for p in self.session.passwords.keys():
                attr = curses.A_NORMAL
                # Highlight requested password
                if p == hl_password:
                    attr = curses.A_STANDOUT
                # string for number of letters. "??" when unknown.
                if self.session.passwords[p] != None:
                    nb_letters = "%02d" % self.session.passwords[p]
                else:
                    nb_letters = "??"
                # Password index used to select password when trying a password
                password_idx = "%d" % (idx + 1)
                # Align right if more than 9 passwords
                if len(self.session.passwords) >= 10 and idx < 9:
                    password_idx = " " + password_idx
                self.item_win.addstr(line_offset + idx, 10,
                                     "%s) %s (%s)" % (password_idx, p, nb_letters),
                                     attr)
                idx = idx + 1
            self.item_win.refresh()

    def display_hl_item(self, itemslist, hl_item):
        """Display item list and highlight a particular one"""
        # Initialize attributes to normal
        itemsattr = [curses.A_NORMAL] * len(itemslist)
        # Highlight requested one
        itemsattr[itemslist.index(hl_item)] = curses.A_STANDOUT
        # Display items with requested
        self.display_items(itemslist, itemsattr)

    def display_items(self, itemslist, itemsattr=None):
        """Display list of items with their corresponding attributes"""
        if itemsattr == None:
            itemsattr = [curses.A_NORMAL] * len(itemslist)
        assert(len(itemslist) == len(itemsattr))
        line_offset = 3
        idx = 0
        self.item_win.clear()
        for item in itemslist:
            attr = itemsattr[idx]
            self.item_win.addstr(line_offset + idx, 10, item, attr)
            idx = idx + 1
        self.item_win.refresh()

    def select_item(self, itemslist):
        """Select an item from item list using arrow keys"""
        assert(len(itemslist) > 0)
        # select first item from the list
        item = itemslist[0]
        self.display_hl_item(itemslist, item)
        # Read user key pressed
        key = self.item_win.getch()
        # Exit when pressing enter
        while key != curses.KEY_ENTER and key != 10 and key != 13:
            if key == curses.KEY_DOWN and item != itemslist[-1]:
               item = itemslist[itemslist.index(item) + 1]
               self.display_hl_item(itemslist, item)
            elif key == curses.KEY_UP and item != itemslist[0]:
               item = itemslist[itemslist.index(item) - 1]
               self.display_hl_item(itemslist, item)
            key = self.item_win.getch()
        self.dbg_print(item + " selected")
        return item


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

def test_menu():
    session = Session()
    session.menu()

def google():
    begin_x = 20
    begin_y = 7
    height = 5
    width = 40
    curses.noecho()
    curses.cbreak()
    win = curses.newwin(height, width, begin_y, begin_x)
    try:
        tb = curses.textpad.Textbox(win)
        text = tb.edit()
        curses.addstr(4,1,text.encode('utf_8'))
    finally:
        curses.endwin()

if __name__ == "__main__":
    pipboy = Pipboy()
    try:
        #pipboy.display_menu()
        for p in passwords:
            pipboy.session.add_password(p)
        #pipboy.display_passwords("FLUID")
        #pipboy.display_hl_item(pipboy.passwords, "FLUID")
        #pipboy.select_item(pipboy.session.passwords.keys())
        pipboy.main_loop()
    finally:
        pipboy.exit()
