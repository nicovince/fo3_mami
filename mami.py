#!/usr/bin/env python
# Solve Mastermind kind of game present in Fallout 3

import sys
import curses
import curses.textpad
import time

class Session:
    def __init__(self):
        # List of dictionnary passwords : [{"password1" : {"n" : 3}}, {"password2": ...}]
        self.passwords = []
        self.password_len = 0

    def has_password(self, passwd):
        """Return True when passwd already present in passwords list"""
        for p in self.passwords:
            if passwd in p.keys():
                return True
        return False

    def add_password(self, passwd):
        """Add a password to the list, initialize number of good positions to None"""
        if not self.has_password(passwd):
            self.passwords.append({passwd : {"n" : None}})
            self.password_len = len(passwd)
        else:
            print "password %s already present in list" % passwd

    def get_passwords(self):
        password_list = []
        for p in self.passwords:
            password_list.append(p.keys()[0])
        return password_list

    def delete_password(self, passwd):
        """Remove a password from the list"""
        #self.passwords.pop(password, None)
        for p in self.passwords:
            if p.keys()[0] == passwd:
                self.passwords.pop(p)
                break

    def get_nb_good_letters(self, passwd):
        for p in self.passwords:
            if passwd in p.keys():
                return p[passwd]["n"]

    def set_nb_good_letters(self, passwd, n):
        """Set number of good letters for password"""
        for p in self.passwords:
            if passwd in p.keys():
                p[passwd]["n"] = n

    def clear_passwords(self):
        """Clear all passwords in current session"""
        self.passwords = []
        self.password_len = 0

    def try_password(self, passwd, n):
        """
        Reccord n as number of good positions for password

        Return True if n is equals to length of passwd
        """
        if self.has_password(passwd):
            if (self.get_nb_good_letters(passwd) != n and
                self.get_nb_good_letters(passwd) is not None):
                print "Password %s already, number of good positions was %d, now set to %d" % (passwd, self.get_nb_good_letters(passwd), n)
        self.set_nb_good_letters(passwd, n)
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
            pa  = p.keys()[0]
            if pa != passwd:
                nb_commons = self.get_nb_common(passwd, pa)
                if nb_commons == n:
                    commons.append(pa)
        return commons

    def get_candidates(self):
        """Based on state of list of passwords and number of good letters, return list of candidates"""
        # Initialize candidates with passwords not tested yet
        candidates = [c for c in self.get_passwords() if self.get_nb_good_letters(c) == None]
        tried_passwords = [p for p in self.get_passwords() if self.get_nb_good_letters(p) != None]
        for p in tried_passwords:
            if len(p) == self.get_nb_good_letters(p):
                candidates = [p]
                break;
            sub_candidates = self.find_common(p, self.get_nb_good_letters(p))
            candidates = [c for c in candidates if c in sub_candidates]
        return candidates

    def autoplay(self, match):
        """Autoplay current session with provided password"""
        candidates = self.get_candidates()
        while len(candidates) != 1:
            trial = candidates[0]
            n = self.get_nb_common(trial, match)
            print "Test %s from %s, got %d good letters"  % (trial, str(candidates), n)
            if self.try_password(trial, self.get_nb_common(trial, match)):
                candidates = [trial]
            else:
                candidates = self.get_candidates()
        print candidates[0]

    def clear_trials(self):
        """Clear trials on list of passwords"""
        for k in self.get_passwords():
            self.passwords[k] = None
            self.set_nb_good_letters(k, None)

    def ui_add_password(self):
        """User interface for adding password to the list"""
        password = raw_input("Add password to the list : ").upper()
        # check length of password
        if len(self.passwords) != 0:
            password_len = len(self.get_passwords()[0])
            while len(password) != password_len:
                print "Wrong password length, expecting %d character" % password_len
                password = raw_input("Add password to the list : ").upper()

        self.add_password(password)

    def ui_try_password(self):
        """User interface to test password"""
        idx = 1
        # List passwords with number of good letters when available
        for p in self.get_passwords():
            if self.get_nb_good_letters(p) != None:
                print "%d) %s : %d good letters" % (idx, p, self.get_nb_good_letters(p))
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
        password = self.get_passwords()[choice - 1]
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
        self.item_win = curses.newwin(y-1, self.x, 1, 0)
        # To be able to do getch() and interpret keypad correctly
        self.stdscr.keypad(1)
        self.item_win.keypad(1)


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
                             "callback" : self.try_password}},
                     {"c" : {"text" : "(c)lear passwords",
                             "callback" : self.clear_passwords}},
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
            self.display_items(self.session.get_passwords())
        self.usr_win.refresh()
        self.display_options(["Enter password candidate"])
        self.item_win.move(3, 10)
        self.text_box_win.refresh()
        password = self.text_box.edit()
        self.session.add_password(password)
        self.text_box_win.clear()
        self.text_box_win.refresh()
        self.display_items(self.session.get_passwords())
        self.clear_menu()

    def try_password(self):
        """Try password, and ask number of good letters"""
        attributes = self.get_passwords_attributes()
        passwords = self.session.get_passwords()
        password = self.select_item(passwords, attributes)
        self.display_options(["How many good letters ? "])
        while True:
            nb_good_letters = self.text_box.edit()
            nb_good_letters = nb_good_letters.strip()
            self.text_box_win.clear()
            self.text_box_win.refresh()
            if (nb_good_letters.isdigit() and
                self.session.check_numerical_choice(nb_good_letters, 0, self.session.password_len)):
                break
            else:
                self.dbg_print("%s not accepted %s" % (nb_good_letters, nb_good_letters.isdigit()))
        self.session.try_password(password, int(nb_good_letters))
        # Redisplay passwords after trial
        attributes = self.get_passwords_attributes()
        self.display_items(passwords, attributes)

    def clear_passwords(self):
        """Clear passwords in current session and on screen"""
        self.session.clear_passwords()
        self.item_win.clear()
        self.item_win.refresh()

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

    def select_item(self, itemslist, attrlist=None):
        """Select an item from item list using arrow keys"""
        assert(len(itemslist) > 0)
        if attrlist == None:
            attrlist = [curses.A_NORMAL] * len(itemslist)
        assert(len(itemslist) == len(attrlist))
        # select first item from the list
        item = itemslist[0]
        selattrlist = list(attrlist)
        selattrlist[itemslist.index(item)] = curses.A_STANDOUT
        # Set cursor
        self.item_win.move(3, 10)
        #self.display_hl_item(itemslist, item)
        self.display_items(itemslist, selattrlist)
        # Read user key pressed
        key = self.item_win.getch()
        # Exit when pressing enter
        while key != curses.KEY_ENTER and key != 10 and key != 13:
            if key == curses.KEY_DOWN and item != itemslist[-1]:
                item = itemslist[itemslist.index(item) + 1]
            elif key == curses.KEY_UP and item != itemslist[0]:
                item = itemslist[itemslist.index(item) - 1]
            selattrlist = list(attrlist)
            selattrlist[itemslist.index(item)] = curses.A_STANDOUT
            self.display_items(itemslist, selattrlist)
            key = self.item_win.getch()
        self.dbg_print(item + " selected")
        return item

    def get_passwords_attributes(self):
        """Get attributes to display each password based on candidacy"""
        # Initialize
        attrlist = [curses.A_NORMAL] * len(self.session.passwords)
        candidates = self.session.get_candidates()
        for p in candidates:
            attrlist[self.session.get_passwords().index(p)] = curses.A_BOLD
        if len(candidates) == 1:
            attrlist[self.session.get_passwords().index(p)] = curses.A_BLINK

        self.dbg_print("candidates : " + str(candidates))
        return attrlist


    def prompt(self, choices=None):
        #self.usr_win.addstr(1, 2, "> ")
        self.text_box_win.clear()
        self.usr_win.refresh()
        usr_input = self.text_box.edit()
        self.stdscr.addstr(0,0, usr_input + " " + str(type(choices[0])))
        self.stdscr.addstr(1,0, str(choices))
        self.stdscr.refresh()
        while usr_input.strip() not in choices:
            self.stdscr.addstr(self.y - 6, 0, "Invalid command")
            self.stdscr.refresh()
            self.text_box_win.clear()
            usr_input = self.text_box.edit()
        return usr_input


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

def test_autoplay():
    session = Session()
    for p in passwords:
        session.add_password(p)
    session.autoplay("FLUID")

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
    test_autoplay()
    #sys.exit(0)
    pipboy = Pipboy()
    try:
        #pipboy.display_menu()
        for p in passwords:
            pipboy.session.add_password(p)
        #pipboy.select_item(pipboy.session.passwords.keys())
        pipboy.main_loop()
    finally:
        pipboy.exit()
