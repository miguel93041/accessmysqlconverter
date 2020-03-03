"""
This module provides the GUI and buttons, etc... functionality for the application
"""


from os import path
from sys import argv

from tkinter import Frame, Label, IntVar, Tk, messagebox, PhotoImage, simpledialog
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.ttk import Progressbar, Checkbutton, Button, Entry

from accessmysqlconverter.accessconnector import Accessconnector, ODBCDriverNotFoundError, AccessConnectionError
from accessmysqlconverter.accesshandler import Accesshandler


module_dir = path.dirname(__file__)
author = "miguel93041"
version = "1.0.4"
title = "AccessMySQLConverter by {} ({})".format(author, version)
icon = path.join(module_dir, 'images\\icon.ico')


class StringDialog(simpledialog._QueryString):
    """Class for overwriting tkinter window icon with mine"""
    def body(self, master):
        super().body(master)
        try:
            self.iconbitmap(icon)
        except Exception as ex:
            messagebox.showerror("Error", ex.args[0])

    @staticmethod
    def ask_string(title_, prompt, **kargs):
        d = StringDialog(title_, prompt, **kargs)
        return d.result


class Application(Frame):
    """Main class, handles GUI and starts logic"""
    def __init__(self, master=None, arguments=()):
        super().__init__(master)

        self._file_path = ""
        self._output_dir = ""
        self._same_dir = IntVar(value=1)        # By default output path is the same as file path
        self._show_password = False

        self._master = master
        self.grid()
        try:
            self._create_widgets()
        except Exception as ex:
            messagebox.showerror("Error", ex.args[0])

        self._same_dir_as_file()        # Disable output button and it sets output dir at start
        self._convert_progressbar.grid_remove()        # Hide loading bar at start

        if self._is_file_path_in_arguments(arguments):
            self._set_file_path(arguments[1])

    @staticmethod
    def _is_file_path_in_arguments(arguments):
        """Method to check if arguments[1] (because arguments[0] is application
        path) is a file path
        """
        if arguments.__len__() > 1:
            file_path = arguments[1]
            if path.isfile(file_path):
                extension = path.splitext(file_path)[1]
                if extension == ".mdb" or extension == ".accdb":
                    return True
        return False

    def _create_widgets(self):
        """GUI building"""
        # File widgets
        self._filename_label = Label(self._master, width="22", anchor="e", text="Access File (*.mdb, *.accdb):")
        self._filename_label.grid(row=0, column=0)

        self._filename_path_label = Label(self._master, width="50", anchor="w", textvariable=self._file_path, bg="#cccccc")
        self._filename_path_label.grid(row=0, column=1)

        self._browse_file_button = Button(self._master, text="...", width="3", command=self._browse_file)
        self._browse_file_button.grid(row=0, column=2)

        # Password widget
        self._password_label = Label(self._master, width="22", anchor="e", text="Password (else leave empty):")
        self._password_label.grid(row=1, column=0)

        self._password_entry = Entry(self._master, width="58", show="*")
        self._password_entry.grid(row=1, column=1)

        self._password_show_image = PhotoImage(file=path.join(module_dir, "images\\watch_pwd.png")).subsample(8, 8)
        self._password_show_button = Button(self._master, width="3", command=self._show_hide_password, image=self._password_show_image)
        self._password_show_button.grid(row=1, column=2)

        # Checkbox widget
        self._same_dir_as_file_checkbox = Checkbutton(self._master, width="50", text="Same directory as source file", var=self._same_dir, command=self._same_dir_as_file)
        self._same_dir_as_file_checkbox.grid(row=2, column=1, pady=8)

        # Output widgets
        self._output_label = Label(self._master, width="22", anchor="e", text="Output directory:")
        self._output_label.grid(row=3, column=0)

        self._output_dir_label = Label(self._master, width="50", anchor="w", textvariable=self._file_path,
                                       bg="#cccccc")
        self._output_dir_label.grid(row=3, column=1)

        self._browse_dir_button = Button(self._master, text="...", width="3", command=self._browse_dir)
        self._browse_dir_button.grid(row=3, column=2)

        # Frame for conversion
        self._convert_frame = Frame(self._master)
        self._convert_frame.grid(row=4, column=0, columnspan=2, pady=5)

        # Convert widget
        self._convert_button = Button(self._convert_frame, width="84", text="CREATE SQL FILE", command=self.convertSQL, state="disabled")
        self._convert_button.grid(row=0, column=0)

        # Progressbar widget
        self._convert_progressbar = Progressbar(self._convert_frame, length="512")
        self._convert_progressbar.grid(row=1, column=0)

    def convertSQL(self):
        """SQL file generator"""
        self._convert_progressbar.grid(row=1, column=0)        # Show progressbar
        self._convert_progressbar["value"] = 0
        self._master.config(cursor="wait")
        accessconnector = Accessconnector()
        try:
            driver = accessconnector.driver(self._file_path)
            con = accessconnector.con(driver, self._file_path, self._get_password())
            self._convert_progressbar["value"] = 33
        except (AccessConnectionError, ODBCDriverNotFoundError) as ex:
            self._master.config(cursor="")
            self._convert_progressbar["value"] = 100
            messagebox.showerror("Error", ex.args[1])
        else:
            cur = con.cursor()
            database_name = StringDialog.ask_string(title_="Database name", prompt="Name for database:")
            if database_name is not None:
                if database_name == "":
                    messagebox.showinfo("Error", "Database name field cannot be blank")
                else:
                    self._convert_progressbar["value"] = 66
                    accesshandler = Accesshandler(cur)
                    accesshandler.make_file(self._output_dir, database_name)
                    messagebox.showinfo("Completed", "SQL file generated successfully")
            cur.close()
            con.close()
            self._master.config(cursor="")
            self._convert_progressbar["value"] = 100

    def _set_file_path(self, file_path):
        """Setter for file path, updates file path label and output dir based on _same_dir"""
        self._file_path = file_path
        self._filename_path_label.config(text=self._file_path)
        if self._is_same_dir() == 1:
            self._set_output_dir(path.dirname(self._file_path))
        if self._file_path != "" and self._output_dir != "":        # Enable convert button if it´s good to go
            self._convert_button.config(state="normal")
        self._update_gui_size()

    def _set_output_dir(self, output_dir):
        """Setter for output dir"""
        self._output_dir = output_dir
        self._output_dir_label.config(text=self._output_dir)
        if self._file_path != "" and self._output_dir != "":        # Enable convert button if it´s good to go
            self._convert_button.config(state="normal")
        self._update_gui_size()

    def _update_gui_size(self):
        """Method for expanding or shrinking GUI based on the length of the paths"""
        min_size = 50        # Standard min-size on creating GUI for _filename_path_label ...
        size = max(self._file_path.__len__(), self._output_dir.__len__())
        if size > min_size:
            self._filename_path_label.config(width=size)
            self._output_dir_label.config(width=size)
            self._same_dir_as_file_checkbox.config(width=size)
            self._password_entry.config(width=int((size * 58) / min_size))
            self._convert_button.config(width=int((size * 84) / min_size))
            self._convert_progressbar.config(length=int((size * 512) / min_size))
        elif size <= min_size:
            self._filename_path_label.config(width=50)
            self._output_dir_label.config(width=50)
            self._same_dir_as_file_checkbox.config(width=50)
            self._password_entry.config(width=58)
            self._convert_button.config(width=84)
            self._convert_progressbar.config(length=512)

    def _same_dir_as_file(self):
        """Functionality for disabling or enabling browse output dir button
        and setting _output_dir based on _file_path
        """
        if self._is_same_dir() == 1:
            self._set_output_dir(path.dirname(self._file_path))
            self._browse_dir_button.config(state="disabled")
        else:
            self._browse_dir_button.config(state="normal")

    def _show_hide_password(self):
        """Show/Hide password by current _show_password value and updates it"""
        if self._show_password:
            self._password_entry.config(show="*")
            try:
                self._password_show_image = PhotoImage(file=path.join(module_dir, "images\\watch_pwd.png")).subsample(8, 8)
            except Exception as ex:
                messagebox.showerror("Error", ex.args[0])
        else:
            self._password_entry.config(show="")
            try:
                self._password_show_image = PhotoImage(file=path.join(module_dir, "images\\hide_pwd.png")).subsample(8, 8)
            except Exception as ex:
                messagebox.showerror("Error", ex.args[0])
        self._password_show_button.config(image=self._password_show_image)
        self._show_password = not self._show_password

    def _browse_file(self):
        """Browse file functionality"""
        file_path = askopenfilename(filetypes=[("Microsoft Access", ".mdb .accdb")])
        if file_path != "":        # If browse window is closed then don´t update
            self._set_file_path(file_path)

    def _browse_dir(self):
        """Browse dir functionality"""
        output_dir = askdirectory()
        if output_dir != "":        # If browse window is closed then don´t update
            self._set_output_dir(output_dir)

    def _get_password(self):
        """Getter for password"""
        return self._password_entry.get()

    def _is_same_dir(self):
        """Getter for _same_dir"""
        return self._same_dir.get()


def main(arguments):
    root = Tk()
    root.configure(relief='flat', borderwidth=10)
    root.resizable(True, False)
    root.title(title)
    try:
        root.iconbitmap(icon)
    except Exception as ex:
        messagebox.showerror("Error", ex.args[0])

    app = Application(master=root, arguments=arguments)
    app.mainloop()


if __name__ == '__main__':
    print(__file__)
    main(argv)
