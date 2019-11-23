#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import patch_ips

class LazyIPS:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("Lazy IPS")
        self.window.set_border_width(5)
        self.window.connect("delete_event", self.close_app)

        self.table = Gtk.Table(7, 4, True)
        self.table.set_row_spacings(2)
        self.table.set_col_spacings(2)
        self.window.add(self.table)

        self.rom_label = Gtk.Label("Select ROM file:")
        self.rom_label.set_alignment(0, 0)
        self.table.attach(self.rom_label, 0, 4, 0, 1)

        self.rom_textEntry = Gtk.Entry()
        self.rom_openFileButton = Gtk.Button("Open file..", Gtk.STOCK_OPEN)
        self.rom_openFileButton.connect("clicked", self.select_rom)
        self.table.attach(self.rom_textEntry, 0, 3, 1, 2)
        self.table.attach(self.rom_openFileButton, 3, 4, 1, 2)

        self.ips_label = Gtk.Label("Select IPS file:")
        self.ips_label.set_alignment(0, 0)
        self.table.attach(self.ips_label, 0, 4, 2, 3)

        self.ips_textEntry = Gtk.Entry()
        self.ips_openFileButton = Gtk.Button("Open file..", Gtk.STOCK_OPEN)
        self.ips_openFileButton.connect("clicked", self.select_ips)
        self.table.attach(self.ips_textEntry, 0, 3, 3, 4)
        self.table.attach(self.ips_openFileButton, 3, 4, 3, 4)

        self.backupCheckBox = Gtk.CheckButton("Create a backup file.")
        self.table.attach(self.backupCheckBox, 0, 4, 4, 5)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.progressbar.set_text("0%")
        self.table.attach(self.progressbar, 0, 4, 5, 6)

        self.runButton = Gtk.Button("Execute", Gtk.STOCK_EXECUTE)
        self.runButton.connect("clicked", self.patch_ips)
        self.exitButton = Gtk.Button("Exit", Gtk.STOCK_QUIT)
        self.exitButton.connect("clicked", self.close_app)

        self.table.attach(self.runButton, 2, 3, 6, 7)
        self.table.attach(self.exitButton, 3, 4, 6, 7)

        self.window.show_all()

    def main(self):
        Gtk.main()

    def close_app(self, widget, data=None):
        Gtk.main_quit()

    def select_rom(self, widget):
        dialog = Gtk.FileChooserDialog("Open ROM", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL,  Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        if dialog.run() == Gtk.ResponseType.OK:
            self.rom_textEntry.set_text(dialog.get_filename())
            self.progressbar.set_text("0%")
            self.progressbar.set_fraction(0)
        dialog.destroy()

    def select_ips(self, widget):
        dialog = Gtk.FileChooserDialog("Open IPS patch", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL,  Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filter = Gtk.FileFilter()
        filter.set_name("IPS patch (*.ips)")
        filter.add_pattern("*.ips")
        dialog.add_filter(filter)
        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        if dialog.run() == Gtk.ResponseType.OK:
            self.ips_textEntry.set_text(dialog.get_filename())
            self.progressbar.set_text("0%")
            self.progressbar.set_fraction(0)
        dialog.destroy()

    def error_message(self, message):
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message)
        dialog.set_title("Error")
        if dialog.run() == Gtk.ResponseType.CLOSE:
            dialog.destroy()

    def patch_ips(self, widget):
        romfile = self.rom_textEntry.get_text()
        if self.backupCheckBox.get_active():
            try:
                os.rename(romfile, romfile + ".bak")
                shutil.copyfile(romfile + ".bak", romfile)
            except:
                self.error_message("Can't create a backup file!")
                return
        try:
            rom = open(romfile, "rb+")
        except IOError:
            self.error_message("File %s not found!" % romfile)
            return
        ipsfile = self.ips_textEntry.get_text()
        try:
            patch_file = open(ipsfile, "rb")
        except IOError:
            self.error_message("File %s not found!" % ipsfile)
            return

        try:
            patchsize = os.path.getsize(ipsfile)
            for patch_line in patch_ips.read_ips_patch(patch_file):
                
                while Gtk.events_pending():
                    Gtk.main_iteration()
                pb_percent = ((patch_file.tell()*100)/patchsize)
                self.progressbar.set_fraction(pb_percent/100.)
                self.progressbar.set_text("%d%%" % (pb_percent))

                patch_ips.apply_patch_line(rom, patch_line)
                
            self.progressbar.set_text("Done!")

        except Exception as err:
            self.error_message(f"Error: {err}")
        finally:
            patch_file.close()
            rom.close()

if __name__ == "__main__":
    app = LazyIPS()
    app.main()
