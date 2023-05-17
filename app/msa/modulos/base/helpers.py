import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class PasswordWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Password")
        self.set_size_request(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.label = Gtk.Label("Passphrase:")
        self.entry = Gtk.Entry()
        self.button = Gtk.Button("OK")
        self.button.connect("clicked", self.on_button_clicked)
        self.entry.set_text("")

        vbox.pack_start(self.label, False, True, 0)
        vbox.pack_start(self.entry, True, True, 0)
        vbox.pack_start(self.button, False, True, 0)
        self.entry.set_visibility(False)
        self.entry.set_activates_default(True)
        self.button.set_can_default(True)
        self.set_default(self.button)
        #self.set_transient_for(Gtk.Widget.get_toplevel(self))
        self.set_modal(True)

    def on_button_clicked(self, widget):
        """
        Oculta la ventana de Password

        Args:
            widget:
        """
        self.hide()


def prompt_password():
    """

    Lanza la ventana de error.
    """

    win = PasswordWindow()
    win.connect("activate-default", Gtk.main_quit)
    win.show_all()
    while win.get_property("visible"):
      Gtk.main_iteration()
    value = win.entry.get_text()
    win.destroy()
    return value


def show_error(message):
    """
    En base al mensaje recibido por parámetro, se mostrará
    una ventana de error.

    Args:
        mensaje (str): Texto que se deberá mostrar.
    """
    dialog = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                               buttons=Gtk.ButtonsType.OK, title="Error")
    dialog.set_markup(message)
    dialog.run()
    dialog.destroy()


if __name__ == "__main__":
    passphrase = prompt_password()
    show_error(passphrase)

