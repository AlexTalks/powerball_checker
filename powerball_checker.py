#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, cmd
from collections import namedtuple

PowerballTicket = namedtuple("PowerballTicket", 
    ["ticket_number", "white_balls", "powerball"])

class PowerballChecker(cmd.Cmd):
    intro_lines = []
    intro_lines.append("💸💸💸 Welcome to the Powerball Checker! 💸💸💸")
    intro_lines.append("⚪ ️⚪ ️⚪ ️⚪ ️⚪ ️🔴".center(len(intro_lines[0]), ' '))
    intro_lines.append("Type start to begin, help or ? to list commands, or exit to stop at any time")

    steps = ['Step 1: Load tickets from a valid CSV file',
        'Step 2: Load Powerball drawing numbers',
        'Step 3: Enjoy your results!']

    intro = '\n'.join(intro_lines + steps)
    prompt = "(🐻 )"     # alternatives: 💩, 🔴, 💰


    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.ticket_file = None
        self.tickets_loaded = False
        self.tickets = []
        self.white_balls = None
        self.powerball = None
        self.won = False
        self.winning_tickets = []
        self.checked = False

        # Cmd aliases
        self.do_tickets = self.do_load
        self.do_quit = self.do_exit
        self.do_end = self.do_exit


    def do_load(self, arg):
        '''Loads tickets from a file.  File should be CSV format, first line is ignored, and columns formatted like:
Ticket Number\t| WB 1\t| WB 2\t| WB 3\t| WB 4\t| WB 5\t| Powerball
-------------\t| ----\t| ----\t| ----\t| ----\t| ----\t| ---------
  12345-6789\t| 32\t| 16\t| 19\t| 57\t| 34\t| 13
'''
        filename = arg
        if not filename:
            print "Ticket file name: ",
            filename = sys.stdin.readline().rstrip()

        if not os.path.isfile(filename):
            print "... Filename \"%s\" is invalid! Cannot open." % filename
        else:
            self.ticket_file = filename
            self.do_reload("")

    def do_reload(self, arg):
        '''Reloads the given tickets file'''
        print "... loading"

        self.tickets = []
        line_num = 0
        error_num = 0

        with open(self.ticket_file) as f:
            header = f.readline()
            for line in f:
                line_num += 1
                cols = line.rstrip().split(',')
                if len(cols) < 7:
                    continue
                try:
                    ticket = PowerballTicket(cols[0].strip(), 
                        [int(cols[1]), int(cols[2]), int(cols[3]), int(cols[4]), int(cols[5])],
                        int(cols[6]))
                    self.tickets.append(ticket)
                except:
                    continue

        print "Read %d tickets, %d of them had errors" % (line_num, error_num)
        if line_num > 0 and error_num < line_num:
            self.tickets_loaded = True
        else:
            print "Too many errors, please try again"

        if self.tickets_loaded:
            print "✅ %d Tickets loaded from file \"%s\" (out of %d)" % (len(self.tickets), 
                self.ticket_file, line_num)


    def do_balls(self, arg):
        '''Loads the Powerball drawing numbers'''
        print "Time to input the balls!  First enter the 5 white balls, followed by the red Powerball:"
        try:
            wb = []
            for i in range(5):
                print "\t⚪ :️",
                ball = int(sys.stdin.readline())
                wb.append(ball)
            print "\t🔴 :",
            pb = int(sys.stdin.readline())

            self.white_balls = sorted(wb)
            self.powerball = pb
        except:
            print "Error inputing drawing numbers, please try again"
            return

        print "✅ Powerball drawing numbers entered!"


    def do_check(self, arg):
        '''Checks your Powerball winnings!'''
        if self.ready_to_check():
            self.check_winnings()
        else:
            print "Not all inputs are loaded.  Still needed:\n---"
            if not self.tickets_loaded:
                print "tickets\t\tLoad tickets from a CSV file with the `load` command."
            if not self.white_balls or len(self.white_balls != 5):
                print "white balls\tLoad white balls drawn with the `balls` command."
            if not self.powerball:
                print "powerball\tLoad Powerball with the `balls` command."


    def ready_to_check(self):
        return (self.tickets_loaded and self.white_balls and 
            len(self.white_balls) == 5 and self.powerball)


    def check_winnings(self):
        self.checked = True
        self.won = False
        self.winning_tickets = []
        for ticket in self.tickets:
            wb = ticket.white_balls
            wb_matches = self.matching_whites(ticket.white_balls, list(self.white_balls))
            prize = self.calculate_prize(wb_matches, ticket.powerball == self.powerball)
            if prize:
                self.winning_tickets.append((ticket, prize))
        if self.won > 0:
            print "💰 GRAND PRIZE WON! 💰"
        elif len(self.winning_tickets) > 0:
            print "💸 Some winning tickets found..."
        else:
            print "Sorry to announce... no tickets have won"

        if len(self.winning_tickets):
            print "Ticket \t\t| Winnings"
            print "----------\t| ---------"
            for ticket in self.winning_tickets:
                print ticket[0].ticket_number, "\t|", ticket[1]


    def matching_whites(self, selected, drawn):
        match = 0
        for number in selected:
            if number in drawn:
                drawn.remove(number)
                match += 1
        return match


    def calculate_prize(self, white_matches, powerball_matched):
        if powerball_matched and white_matches == 5:
            self.won = True
            return "💸💸💸 GRAND PRIZE 💸💸💸"
        elif white_matches == 5:
            return "$1,000,000"
        elif powerball_matched and white_matches == 4:
            return "$50,000"
        elif white_matches == 4 or (powerball_matched and white_matches == 3):
            return "$100"
        elif white_matches == 3 or (powerball_matched and white_matches == 2):
            return "$7"
        elif powerball_matched:
            return "$4"
        else:
            return None


    def do_start(self, arg):
        '''Starts Powerball checker from the beginning'''
        self.do_load("")
        if self.tickets_loaded:
            self.do_balls("")
        if self.ready_to_check():
            self.check_winnings()


    def do_steps(self, arg):
        '''Prints program steps'''
        for step in PowerballChecker.steps:
            print step


    def do_exit(self, arg):
        '''Quits program'''
        return self.end_program()


    def end_program(self):
        print "Thank you for playing Powerball!"
        if self.won:
            print "Congratulations on winning! 💸"
        elif len(self.winning_tickets) > 0:
            print "Some congrats are in order..."
        elif(self.checked):
            print "Sorry that you lost! 😭"
        return True


if __name__ == "__main__":
    PowerballChecker(sys.argv).cmdloop()
