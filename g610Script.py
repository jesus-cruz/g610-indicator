
import sys
import os.path
import imp
import time
import signal
import usb.core
import usb.util
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from time import sleep

dev = None
intf = None
data = []

g610_brightness = [
  "000000",
  "424242",
  "818181",
  "c0c0c0",
  "ffffff"
]

g610_backlitmode_static       = "11ff0d3b0001#brightness#0200000000000000000000"
g610_backlitmode_logo_static  = "11ff0d3b0101#brightness#0200000000000000000000"

APPINDICATOR_ID = 'g610_backlit'

def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('lgs-icon.png'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()

def build_menu():
    menu = gtk.Menu()

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)

    item_zero = gtk.MenuItem('0')
    item_zero.connect('activate', change_to_level_zero)

    item_one = gtk.MenuItem('1')
    item_one.connect('activate', change_to_level_one)

    item_two = gtk.MenuItem('2')
    item_two.connect('activate', change_to_level_two)

    item_three = gtk.MenuItem('3')
    item_three.connect('activate', change_to_level_three)

    item_four = gtk.MenuItem('4')
    item_four.connect('activate', change_to_level_four)

    menu.append(item_zero)
    menu.append(item_one)
    menu.append(item_two)
    menu.append(item_three)
    menu.append(item_four)
    menu.append(item_quit)

    menu.show_all()
    return menu

def change_to_level_zero(source):
    change_to_level(0)

def change_to_level_one(source):
    change_to_level(1)

def change_to_level_two(source):
    change_to_level(2)

def change_to_level_three(source):
    change_to_level(3)

def change_to_level_four(source):
    change_to_level(4)

def change_to_level( level ):

  data.append(g610_backlitmode_static.replace("#brightness#", g610_brightness[level]))
  data.append(g610_backlitmode_logo_static.replace("#brightness#", g610_brightness[level]))

  attachKeyboard()
  updateKeyboard()
  detachKeyboard()

def attachKeyboard():
  global dev
  global intf
  dev = usb.core.find(idVendor=0x046d, idProduct=0xc333)
  if dev is None:
    print('Device not found'    )
    return
  intf = 1
  if dev.is_kernel_driver_active(intf) is True:
    dev.detach_kernel_driver(intf)
    usb.util.claim_interface(dev, intf)


def detachKeyboard():
  global dev
  global intf
  if intf is not None:
    usb.util.release_interface(dev, intf)
    dev.attach_kernel_driver(intf)
    dev = None
    intf = None


def updateKeyboard():
  global dev
  global data
  try:
    for item in data:
      encoded_data = [ int(''.join([item[i], item[i+1]]), base=16) for i in range(0, len(item), 2)]
      dev.ctrl_transfer(0x21,0x09,0x0211,1,encoded_data)
      sleep(.01)

  except:
    print('Error updating keyboard')


def quit(source):
    gtk.main_quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
