from frequency_analysis_text.functionality import AnalysisText, InvalidFileFormatError, EmptyFileError
from frequency_analysis_text.main import show_info_commands
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image


class MyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Analysis text')
        self.root.geometry('800x500')
        self.root.configure(background='gray')

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.soft_green = '#66cc66'
        self.soft_red = '#cc6666'

        self.btn_font1 = ('Helvetica', 10, 'bold')
        self.btn_font2 = ('Helvetica', 9, 'bold')
        self.txt_font = ('Times New Roman', 12)
        self.ent_font = ('Verdana', 11, 'bold')
        self.lab_and_txt_2_font = ('Consolas', 11)

        self.btn_redo = None
        self.redo_icon = None
        self.btn_undo = None
        self.undo_icon = None
        self.help_menu = None
        self.ent_new_word = None
        self.btn_replace_word = None
        self.scrollbar_text_x = None
        self.scrollbar_text_y = None
        self.scrollbar_log = None
        self.txt_text = None
        self.ent_search_word = None
        self.btn_search_word = None
        self.frm_search = None
        self.txt_log_command = None
        self.dict_commands = None
        self.frm_command = None
        self.btn_load_file = None
        self.lab_path_to_file = None
        self.frm_load_file = None
        self.buttons = {}

        self.obj_text = None

        self.create_widgets()

    def create_widgets(self):
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Command info", command=self.show_help)

        self.frm_load_file = tk.Frame(self.root, height=25, background='gray')
        self.frm_load_file.pack(fill=tk.X, pady=(5, 10))

        self.frm_load_file.columnconfigure([0, 1], weight=1)

        self.lab_path_to_file = tk.Label(self.frm_load_file, text='Path to file...', anchor='w', bg='lightgray',
                                         font=self.lab_and_txt_2_font)
        self.lab_path_to_file.grid(row=0, column=0, padx=5, columnspan=2, sticky='we')

        self.btn_load_file = tk.Button(self.frm_load_file, text='Load file', width=8, bg='lightgray',
                                       command=self.load_file, activebackground='lightgray', font=self.btn_font2)
        self.btn_load_file.grid(row=0, column=2, padx=5)

        self.frm_command = tk.Frame(self.root, height=200, bg='gray', borderwidth=5, relief=tk.GROOVE)
        self.frm_command.pack(fill=tk.X, padx=5)

        self.frm_command.columnconfigure(4, weight=1)

        self.dict_commands = {'Smart mode': ((0, 0), self.smart_mode), 'Root mode': ((0, 1), self.root_mode),
                              'To pickle': ((0, 2), self.save_to_pickle), 'Remove': ((0, 3), self.remove_words),
                              'Case sens': ((1, 0), self.case_sens), 'Restart': ((1, 1), self.restart_text),
                              'To json': ((1, 2), self.save_to_json), 'Result': ((1, 3), self.update_result)}
        for name, row_col_com in self.dict_commands.items():
            b = tk.Button(self.frm_command, text=name, width=10, height=3, background='lightgray',
                          command=row_col_com[1], activebackground='lightgray', font=self.btn_font1)
            b.grid(row=row_col_com[0][0], column=row_col_com[0][1], padx=(5, 10), pady=5)
            self.buttons.update({name: b})

        self.txt_log_command = tk.Text(self.frm_command, height=7.5, bg='green', background='lightgray', wrap=tk.WORD,
                                       font=self.lab_and_txt_2_font)
        self.txt_log_command.grid(row=0, column=4, rowspan=2, padx=(10, 5), pady=5, sticky='ew')

        self.frm_search = tk.Frame(self.root, background='gray', height=25)
        self.frm_search.pack(pady=(10, 0), fill=tk.X)

        self.frm_search.columnconfigure([1, 5], weight=1)

        self.btn_search_word = tk.Button(self.frm_search, text='Search word', width=15, background='lightgray',
                                         command=self.search, activebackground='lightgray', font=self.btn_font2)
        self.btn_search_word.grid(row=0, column=0, padx=(15, 5), sticky='w')

        self.ent_search_word = tk.Entry(self.frm_search, background='lightgray', font=self.ent_font)
        self.ent_search_word.grid(row=0, column=1, padx=(0, 20), sticky='we')

        im = Image.open('undo.png').resize((20, 20))
        self.undo_icon = ImageTk.PhotoImage(image=im)

        # noinspection PyTypeChecker
        self.btn_undo = tk.Button(self.frm_search, image=self.undo_icon, width=25, height=25, bg='lightgray',
                                  activebackground='lightgray', command=self.undo)
        self.btn_undo.grid(row=0, column=2, padx=(0, 10), sticky='w')

        im = Image.open('redo.png').resize((20, 20))
        self.redo_icon = ImageTk.PhotoImage(image=im)

        # noinspection PyTypeChecker
        self.btn_redo = tk.Button(self.frm_search, image=self.redo_icon, width=25, height=25, bg='lightgray',
                                  activebackground='lightgray', command=self.redo)
        self.btn_redo.grid(row=0, column=3, padx=(0, 20), sticky='e')

        self.btn_replace_word = tk.Button(self.frm_search, text='Replace', width=15, background='lightgray',
                                          command=self.replace_words, activebackground='lightgray', font=self.btn_font2)
        self.btn_replace_word.grid(row=0, column=4, padx=(0, 5), sticky='e')

        self.ent_new_word = tk.Entry(self.frm_search, background='lightgray', font=self.ent_font)
        self.ent_new_word.grid(row=0, column=5, padx=(0, 15), sticky='ew')

        self.txt_text = tk.Text(self.root, background='lightgray', wrap=tk.WORD, relief=tk.SUNKEN, borderwidth=5,
                                font=self.txt_font)
        self.txt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.txt_text.tag_config('light', background='yellow')

    def undo(self):
        if self.obj_text:
            self.text_on()
            mess = 'Press "Restart" to return original text.'
            if self.obj_text.history:
                el = self.obj_text.history.pop(-1)
                self.obj_text.redo_stack.append(self.obj_text.text)
                self.obj_text.text = el
                self.txt_text.replace('1.0', tk.END, self.obj_text.text)
                mess = 'Successful undo.'
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def redo(self):
        if self.obj_text:
            self.text_on()
            mess = 'Not successful redo.'
            if self.obj_text.redo_stack:
                el = self.obj_text.redo_stack.pop(-1)
                self.obj_text.history.append(self.obj_text.text)
                self.obj_text.text = el
                self.txt_text.replace('1.0', tk.END, self.obj_text.text)
                mess = 'Successful redo.'
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    @staticmethod
    def show_help():
        messagebox.showinfo('Help', show_info_commands(True))

    def text_off(self):
        self.txt_text.config(state='disabled')
        self.txt_log_command.config(state='disabled')

    def text_on(self):
        self.txt_text.config(state='normal')
        self.txt_log_command.config(state='normal')

    def update_result(self):
        if self.obj_text:
            self.text_on()
            self.txt_text.replace('1.0', tk.END, self.obj_text.text)
            self.txt_log_command.replace('1.0', tk.END, str(self.obj_text))
            self.text_off()

    def root_mode(self):
        if self.obj_text:
            self.text_on()
            if not self.obj_text.root_mode:
                mess = self.obj_text.root_mode_on()
                self.buttons['Root mode'].config(bg=self.soft_green, activebackground=self.soft_green)
                self.buttons['Case sens'].config(bg=self.soft_red, activebackground=self.soft_red)
                self.buttons['Smart mode'].config(bg=self.soft_red, activebackground=self.soft_red)
            else:
                mess = self.obj_text.root_mode_off()
                self.buttons['Root mode'].config(bg=self.soft_red, activebackground=self.soft_red)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def smart_mode(self):
        if self.obj_text:
            self.text_on()
            if not self.obj_text.smart_mode:
                mess = self.obj_text.smart_mode_on()
                self.buttons['Smart mode'].config(bg=self.soft_green, activebackground=self.soft_green)
                self.buttons['Case sens'].config(bg=self.soft_red, activebackground=self.soft_red)
                self.buttons['Root mode'].config(bg=self.soft_red, activebackground=self.soft_red)
            else:
                mess = self.obj_text.smart_mode_off()
                self.buttons['Smart mode'].config(bg=self.soft_red, activebackground=self.soft_red)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def case_sens(self):
        if self.obj_text:
            self.text_on()
            if not self.obj_text.case_sensitive:
                mess = self.obj_text.case_sens_on()
                self.buttons['Case sens'].config(bg=self.soft_green, activebackground=self.soft_green)
                self.buttons['Smart mode'].config(bg=self.soft_red, activebackground=self.soft_red)
                self.buttons['Root mode'].config(bg=self.soft_red, activebackground=self.soft_red)
            else:
                mess = self.obj_text.case_sens_off()
                self.buttons['Case sens'].config(bg=self.soft_red, activebackground=self.soft_red)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def restart_text(self):
        if self.obj_text and messagebox.askquestion('Restart', 'Are you sure you want to restart the '
                                                               'text?') == 'yes':
            self.text_on()
            mess = self.obj_text.restart_user_text()
            self.txt_text.replace('1.0', tk.END, self.obj_text.text)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def remove_words(self):
        if self.obj_text and messagebox.askquestion('Remove', 'Are you sure you want '
                                                              'to remove selected word from the text?') == 'yes':
            self.text_on()
            mess = self.obj_text.remove_or_replace_last_words()
            self.txt_text.replace('1.0', tk.END, self.obj_text.text)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def replace_words(self):
        new_word = self.ent_new_word.get().strip()
        if self.obj_text and messagebox.askquestion('Replace', f'Are you sure you want to replace the '
                                                               f'selected word with "{new_word}"'
                                                               f' from the text?') == 'yes':
            self.text_on()
            mess = self.obj_text.remove_or_replace_last_words(new_word)
            self.ent_new_word.delete(0, tk.END)
            self.txt_text.replace('1.0', tk.END, self.obj_text.text)
            self.txt_log_command.replace('1.0', tk.END, mess)
            self.text_off()

    def search(self):
        if self.obj_text:
            self.text_on()
            tag = False
            word = self.ent_search_word.get().strip()
            mess_for_text = self.obj_text.text
            mess_for_log, *list_index_and_for_log = self.obj_text.search_word(word, True)
            if not mess_for_log.endswith('" - not exist in text.') and mess_for_log != 'Enter a word for search.':
                tag = True
                mess_for_text = mess_for_log
                mess_for_log = list_index_and_for_log[1]
            self.ent_search_word.delete(0, tk.END)
            self.txt_log_command.replace('1.0', tk.END, mess_for_log)
            self.txt_text.replace('1.0', tk.END, mess_for_text)
            if tag:
                for start, end in list_index_and_for_log[0]:
                    start_index = f"1.0+{start}c"
                    end_index = f"1.0+{end}c"
                    self.txt_text.tag_add('light', start_index, end_index)
            self.text_off()

    def save_to_pickle(self):
        if self.obj_text:
            quest = ('If a file with the same name exists, this file will be recorded with a unique identifier.'
                     '\nAre you sure you want to save the pickle file again?')
            save = 'yes'
            if self.buttons['To pickle']['bg'] == self.soft_green:
                save = messagebox.askquestion('Save to pickle', quest)
            if save == 'yes':
                self.text_on()
                mess = self.obj_text.save_file_to_pickle()
                self.txt_log_command.replace('1.0', tk.END, mess)
                self.buttons['To pickle'].config(bg=self.soft_green, activebackground=self.soft_green)
                self.text_off()

    def save_to_json(self):
        if self.obj_text:
            quest = ('If a file with the same name exists, this file will be recorded with a unique identifier.'
                     '\nAre you sure you want to save the json file again?')
            save = 'yes'
            if self.buttons['To json']['bg'] == self.soft_green:
                save = messagebox.askquestion('Save to json', quest)
            if save == 'yes':
                self.text_on()
                mess = self.obj_text.save_file_to_json()
                self.txt_log_command.replace('1.0', tk.END, mess)
                self.buttons['To json'].config(bg=self.soft_green, activebackground=self.soft_green)
                self.text_off()

    def return_all(self):
        self.ent_new_word.delete(0, tk.END)
        self.ent_search_word.delete(0, tk.END)
        self.buttons['Case sens'].config(bg='lightgray', activebackground='lightgray')
        self.buttons['Smart mode'].config(bg='lightgray', activebackground='lightgray')
        self.buttons['Root mode'].config(bg='lightgray', activebackground='lightgray')
        self.buttons['To json'].config(bg='lightgray', activebackground='lightgray')
        self.buttons['To pickle'].config(bg='lightgray', activebackground='lightgray')
        self.txt_text.delete('1.0', tk.END)

    def if_error_load_file(self, file_path):
        self.obj_text = None
        self.lab_path_to_file.config(text=file_path, background=self.soft_red)

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Select a file",
                                               filetypes=(("Text files", "*.txt"), ("Pickle files", "*.pkl *.pickle"),
                                                          ("JSON files", "*.json")))
        try:
            if file_path:
                self.text_on()
                self.return_all()
                self.obj_text = AnalysisText(file_path)
                self.obj_text.load_file(True)
                self.txt_log_command.replace('1.0', tk.END, str(self.obj_text))
                self.txt_text.replace('1.0', tk.END, self.obj_text.text)
                self.lab_path_to_file.config(text=file_path, background=self.soft_green)
        except (PermissionError, FileNotFoundError):
            self.if_error_load_file(file_path)
            self.txt_log_command.replace('1.0', tk.END, 'File not found or access denied.')
        except (EmptyFileError, InvalidFileFormatError, IOError) as e:
            self.if_error_load_file(file_path)
            self.txt_log_command.replace('1.0', tk.END, (str(e)))
        except (AttributeError, KeyError):
            self.if_error_load_file(file_path)
            self.txt_log_command.replace('1.0', tk.END, 'The file is corrupted.')
        finally:
            self.text_off()


if __name__ == '__main__':
    app = MyApp()
    app.root.mainloop()
