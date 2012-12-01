#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Name: lazy_ips.py
#Version (last modification): 19.02.2012
#Copyright (c) 2012 Boris Timofeev <mashin87@gmail.com> www.emunix.org
#License: GNU GPL v3

import os, shutil
import pygtk
pygtk.require('2.0')
import gtk

class LazyIPS:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Lazy IPS")
        self.window.set_border_width(5)
        self.window.connect("delete_event", self.close_app)

        self.table = gtk.Table(7, 4, True)
        self.table.set_row_spacings(2)
        self.table.set_col_spacings(2)
        self.window.add(self.table)

        self.rom_label = gtk.Label("Select ROM file:")
        self.rom_label.set_alignment(0, 0)
        self.table.attach(self.rom_label, 0, 4, 0, 1)

        self.rom_textEntry = gtk.Entry()
        self.rom_openFileButton = gtk.Button("Open file..", gtk.STOCK_OPEN)
        self.rom_openFileButton.connect("clicked", self.select_rom)
        self.table.attach(self.rom_textEntry, 0, 3, 1, 2)
        self.table.attach(self.rom_openFileButton, 3, 4, 1, 2)

        self.ips_label = gtk.Label("Select IPS file:")
        self.ips_label.set_alignment(0, 0)
        self.table.attach(self.ips_label, 0, 4, 2, 3)

        self.ips_textEntry = gtk.Entry()
        self.ips_openFileButton = gtk.Button("Open file..", gtk.STOCK_OPEN)
        self.ips_openFileButton.connect("clicked", self.select_ips)
        self.table.attach(self.ips_textEntry, 0, 3, 3, 4)
        self.table.attach(self.ips_openFileButton, 3, 4, 3, 4)

        self.backupCheckBox = gtk.CheckButton("Create a backup file.")
        self.table.attach(self.backupCheckBox, 0, 4, 4, 5)

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_text("0%")
        self.table.attach(self.progressbar, 0, 4, 5, 6)

        self.runButton = gtk.Button("Execute", gtk.STOCK_EXECUTE)
        self.runButton.connect("clicked", self.patch_ips)
        self.exitButton = gtk.Button("Exit", gtk.STOCK_QUIT)
        self.exitButton.connect("clicked", self.close_app)

        self.table.attach(self.runButton, 2, 3, 6, 7)
        self.table.attach(self.exitButton, 3, 4, 6, 7)

        self.window.show_all()

    def main(self):
        gtk.main()
		
    def close_app(self, widget, data=None):
        gtk.main_quit()

    def select_rom(self, widget):
        dialog = gtk.FileChooserDialog("Open ROM", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,  gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        if dialog.run() == gtk.RESPONSE_OK:
            self.rom_textEntry.set_text(dialog.get_filename())
            self.progressbar.set_text("0%")
            self.progressbar.set_fraction(0)
        dialog.destroy()

    def select_ips(self, widget):
        dialog = gtk.FileChooserDialog("Open IPS patch", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,  gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("IPS patch (*.ips)")
        filter.add_pattern("*.ips")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        if dialog.run() == gtk.RESPONSE_OK:
            self.ips_textEntry.set_text(dialog.get_filename())
            self.progressbar.set_text("0%")
            self.progressbar.set_fraction(0)
        dialog.destroy()
		
    def error_message(self, message):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL |
gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
        dialog.set_title("Error")
        if dialog.run() == gtk.RESPONSE_CLOSE:
            dialog.destroy()

    def patch_ips(self, widget):
        romfile = self.rom_textEntry.get_text()
        if self.backupCheckBox.get_active():
            try:
                shutil.copyfile(romfile, romfile + ".bak")
            except:
                self.error_message("Can't create a backup file!")
                return
        try:
            rom = open(romfile, "r+")
        except IOError:
            self.error_message("File %s not found!" % romfile)
            return
        ipsfile = self.ips_textEntry.get_text()
        try:
            patch = open(ipsfile, "r+")
        except IOError:
            self.error_message("File %s not found!" % ipsfile)
            return
        data = patch.read(5)
        if data != "PATCH":
            self.error_message("IPS file is unknown format.")
            rom.close()
            patch.close()
            return

        patchsize = os.path.getsize(ipsfile)
        while 1:
            data = patch.read(3)
            while gtk.events_pending():
                gtk.main_iteration()
            pb_percent = ((patch.tell()*100)/patchsize)
            self.progressbar.set_fraction(pb_percent/100.)
            self.progressbar.set_text(unicode(pb_percent) + "%")
            if data == "" or data == "EOF":
                rom.close()
                patch.close()
                self.progressbar.set_text("Done!")			
                break
            try:
                address = ord(data[0:1])*256*256 + ord(data[1:2])*256 + ord(data[2:3])
            except:
                self.error_message("Address error")
                rom.close()
                patch.close()
                break
            try:
                rom.seek(address)
            except:
                rom.seek(0, 2)
            data = patch.read(2)
            try:
                length = ord(data[0:1])*256 + ord(data[1:2])
            except:
                self.error_message("Length error")
                rom.close()
                patch.close()
                break
            if length:
                data = patch.read(length)
                rom.write(data)
            else: # RLE
                data = patch.read(2)
                try:
                    length = ord(data[0:1]) * 256 + ord(data[1:2])
                except:
                    self.error_message("Length error 2")
                    rom.close()
                    patch.close()
                    break
                byte = patch.read(1)
                rom.write(byte * length)

if __name__ == "__main__":
    app = LazyIPS()
    app.main()
