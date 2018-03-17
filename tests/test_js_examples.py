import sublime
from unittest import TestCase

version = sublime.version()


class TestJSExamples(TestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def goToLine(self, line):
        self.view.run_command("goto_line", {"line": line})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row - 1, 0)))

    def test_align_js1(self):
        string = """var x = {
    foo: "hello",
    someLongProp: "some other value",
       x: { x: 12, y: 13 }
};"""
        self.setText(string)
        self.goToLine(4)
        self.view.run_command("align_tab", {"user_input": "(?<=:) /l0l1f"})

        row = self.getRow(4)
        self.assertEqual(row, "    x:           { x: 12, y: 13 }")

    def test_align_js2(self):
        string = """var express = require('express'),
http = require('http'),
path = require('path'),
jadebrowser = require('jade-browser');"""
        self.setText(string)
        self.goToLine(4)
        self.view.run_command("align_tab", {"user_input": r"^\s*(?:var)?\s*\S|=/lr0llf2"})
        row = self.getRow(4)
        self.assertEqual(row, "    jadebrowser = require('jade-browser');")
