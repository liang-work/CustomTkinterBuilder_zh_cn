import json
import shutil
import tkinter.messagebox
import uuid
from tkinter.colorchooser import askcolor
import userpaths
from icecream import ic

from properties import PropertiesManager
from tkinter.filedialog import asksaveasfilename, askdirectory
from customtkinter import *
from dragndrop import DragManager
from Widgets.Button import Button
from Widgets.Label import Label
from Widgets.Frame import Frame
from Widgets.Entry import Entry
from Widgets.Switch import Switch
from Widgets.TextBox import TextBox
from Widgets.ProgressBar import ProgressBar
from Widgets.SegmentedButton import SegmentedButton
from Widgets.Slider import Slider
from Widgets.OptionMenu import OptionMenu
from Widgets.CheckBox import CheckBox
from Widgets.ScrollableFrame import ScrollableFrame
from Widgets.RadioButton import RadioButton
from Widgets.Scrollbar import Scrollbar
from Widgets.ComboBox import ComboBox
from Widgets.Main import Main
from CodeGenerator import CodeGenerator
from CustomtkinterCodeViewer import CTkCodeViewer
from PIL import Image

class ThemeUtl:
    def __init__(self, theme_dir, theme_name):
        path = os.path.join(theme_dir, f"{theme_name}.json")
        with open(path, "r") as f:
            self.theme = json.load(f)
        self.path = path
        self.name = theme_name

    def get_theme_by_name(self):
        return self.theme

class SaveFileDialog(CTkToplevel):
    def __init__(self, *args, callback, **kwargs):
        super().__init__(*args, **kwargs)
        #self.pack_propagate(False)
        self.callback = callback
        self.geometry("500x280+600+200")

        self.project_name_lbl = CTkLabel(self, text="Project Name", anchor="w", padx=5, font=CTkFont(size=20))
        self.project_name_lbl.pack(pady=(20, 0), padx=20, fill="x")

        self.project_name_entry = CTkEntry(self, placeholder_text="Enter Project Name")
        self.project_name_entry.pack(padx=20, pady=10, fill="x")
        self.project_name_entry.insert(0, "Untitled")

        self.fr = CTkFrame(self, fg_color="transparent")
        self.fr.pack(fill="x")

        self.dir_lbl = CTkLabel(self.fr, text="Location", anchor="w", padx=5, font=CTkFont(size=20))
        self.dir_lbl.pack(pady=(20, 10), padx=20, fill="x")

        self.dir_entry = CTkEntry(self.fr)
        self.dir_entry.pack(padx=(20, 5), pady=(0, 20), fill="x", side="left", expand=True)
        self.dir_entry.insert(0, userpaths.get_my_documents())
        self.dir_entry.configure(state="disabled")

        self.select_dir = CTkButton(self.fr, text="...", width=20, command=self.choose_dir)
        self.select_dir.pack(side="right", padx=(0, 20), pady=(0, 20))

        self.save_btn = CTkButton(self, text="Save", height=35, command=lambda: (self.callback(dir_=self.dir_entry.get(), name=self.project_name_entry.get()), self.destroy()))
        self.save_btn.pack(fill="x", padx=20, pady=20)

    def choose_dir(self):
        dir = askdirectory()
        if dir != "":
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, dir)
            self.dir_entry.configure(state="disabled")



class MainWindow:
    def __init__(self, root, theme_name):
        self.type = "ROOT"
        self.widgets = {}
        self.id_mapped_widgets = {}
        self.hierarchy = None
        self.r = root
        self.widgets[root] = {}
        self.drag_manager = None
        self.properties = None
        self._parents = []
        self.temp_widgets = {}
        self.file = ""
        self.total_num = 0
        self.files_to_copy = []
        self.title = "Window"
        self.theme_manager = ThemeUtl(theme_dir=f"Themes", theme_name=theme_name)
        self.theme = self.theme_manager.get_theme_by_name()
        self.widget_colors = {
            "CTk": ["fg_color"],
            "CTkToplevel": ["fg_color"],
            "CTkFrame": ["fg_color", "border_color"],
            "CTkButton": ["fg_color", "hover_color", "border_color", "text_color", "text_color_disabled"],
            "CTkLabel": ["fg_color", "text_color"],
            "CTkEntry": ["fg_color", "border_color", "text_color", "placeholder_text_color"],
            "CTkCheckBox": ["fg_color", "border_color", "hover_color", "checkmark_color", "text_color", "text_color_disabled"],
            "CTkSwitch": ["fg_color", "progress_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkRadioButton": ["fg_color", "border_color", "hover_color", "text_color", "text_color_disabled"],
            "CTkProgressBar": ["fg_color", "progress_color", "border_color"],
            "CTkSlider": ["fg_color", "progress_color", "button_color", "button_hover_color"],
            "CTkOptionMenu": ["fg_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkComboBox": ["fg_color", "border_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkScrollbar": ["fg_color", "button_color", "button_hover_color"],
            "CTkSegmentedButton": ["fg_color", "selected_color", "selected_hover_color", "unselected_color", "unselected_hover_color", "text_color", "text_color_disabled"],
            "CTkTextbox": ["fg_color", "border_color", "text_color", "scrollbar_button_color", "scrollbar_button_hover_color"],
            "CTkScrollableFrame": ["label_fg_color"],
            "DropdownMenu": ["fg_color", "hover_color", "text_color"]
        }

    def change_appearance_mode(self, mode):
        wgts = list(self.id_mapped_widgets.values())

        if mode == 0:
            mode = "light"
        else:
            mode = "dark"

        self.r._set_appearance_mode(mode)
        self.loop_change_appearance(mode, self.widgets[self.r])
        #for widget in wgts:
        #    widget._set_appearance_mode(mode)

    def loop_change_appearance(self, mode, d):
        for x in list(d.keys()):

            if d[x] != {}:
                #btn = CTkButton(self, text=x.type, command=lambda x=x: x.on_drag_start(None))
                x._set_appearance_mode(mode)
                self.loop_change_appearance(mode, d[x])
            else:
                x._set_appearance_mode(mode)

    def apply_theme_to_widget(self, widget):
        x = self.theme[widget.get_class()]



        for key in list(x.keys()):
            if key == "top_fg_color":

                if widget.get_class() == "CTkFrame":
                    if widget.master._fg_color == x["fg_color"]:
                        widget.configure(fg_color=x["top_fg_color"])
                        print("top")
                    else:
                        widget.configure(fg_color=x["fg_color"])
                        print("bottom")
            else:
                d = {key: x[key]}
                widget.configure(**d)
        if widget.__class__ not in [Frame, ProgressBar, Scrollbar, Slider, Main]:
            for y in list(self.theme["CTkFont"].keys()):
                if sys.platform == "darwin":
                    d = {"font": CTkFont(family=self.theme["CTkFont"]["macOS"]["family"], size=self.theme["CTkFont"]["macOS"]["size"],
                                      weight=self.theme["CTkFont"]["macOS"]["weight"])}
                elif sys.platform.startswith("win"):
                    d = {"font": CTkFont(family=self.theme["CTkFont"]["Windows"]["family"], size=self.theme["CTkFont"]["Windows"]["size"],
                                      weight=self.theme["CTkFont"]["Windows"]["weight"])}
                else:
                    d = {"font": CTkFont(family=self.theme["CTkFont"]["Linux"]["family"], size=self.theme["CTkFont"]["Linux"]["size"],
                                      weight=self.theme["CTkFont"]["Linux"]["weight"])}
            widget.configure(**d)

        if widget.__class__ in [ComboBox, OptionMenu]:
            widget.set_nonvisible_disable()


    def change(self, **kwargs):
        for key in list(kwargs.keys()):
            if key == "title":
                self.title = kwargs[key]

    def run_code(self):

        code = CodeGenerator(indentation="\t")
        code.add_line(f"""
root = CTkToplevel()
root.title("{self.escape_special_chars(self.title)}")
root.geometry("{self.r.cget('width')}x{self.r.cget('height')}")
root.protocol("WM_DELETE_WINDOW", lambda root=root: (set_default_color_theme("blue"), root.destroy()))
root.configure(fg_color={self.r.cget("fg_color")})
set_default_color_theme("{self.theme_manager.name}")
""")
        self.loop_generate(d=self.widgets[self.r], parent="root", code=code, run=True)
        #print(code.get_code())
        # I know this is not that safe. Do create an issue if there are any safer ways to do this
        exec(code.get_code())

    def export(self, code):
        filename = asksaveasfilename(filetypes=[(".py", "py")])
        if filename != "":
            with open(filename, "w") as f:
                f.write(code)


    def export_code(self):
        code = CodeGenerator(indentation="    ")
        code.add_line(f"""
from customtkinter import *
from PIL import Image

set_default_color_theme("{self.theme_manager.name}")

root = CTk()
root.title("{self.escape_special_chars(self.title)}")
root.geometry("{self.r.cget('width')}x{self.r.cget('height')}")
root.configure(fg_color={self.r.cget("fg_color")})
""")
        self.loop_generate(d=self.widgets[self.r], parent="root", code=code)
        code.add_line("root.mainloop()")

        oop_code = CodeGenerator(indentation="    ")
        oop_code.add_line("""
from customtkinter import *
from PIL import Image

class Root(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
""")
        oop_code.indent()
        oop_code.indent()
        self.loop_generate_oop(d=self.widgets[self.r], parent="self", code=oop_code)
        oop_code.add_line(f"""
set_default_color_theme("{self.theme_manager.name}")
app = Root()
app.geometry("{self.r.cget("width")}x{self.r.cget("height")}")
app.title("{self.escape_special_chars(self.title)}")
app.configure(fg_color={self.r.cget("fg_color")})
app.mainloop()
            """)

        top = CTkToplevel()
        top.geometry("1000x800+500+100")
        top.title("Export Code")
        top.configure(fg_color=["gray95", "gray10"])

        self.codeviewer = CTkCodeViewer.CTkCodeViewer(top, code=oop_code.get_code(), language="python", theme="monokai", font=CTkFont(size=20))
        self.codeviewer.configure(wrap="none")
        self.codeviewer.pack(expand=True, fill="both", padx=20, pady=20)

        self.oop_code_switch = CTkSwitch(top, text="OOP Code", command=self.change_oop)
        self.oop_code_switch.pack(side="left", padx=20, pady=(0, 20))
        self.oop_code_switch.select()

        exp_btn = CTkButton(top, text="Export Code", command=lambda: self.export(self.current.get_code()))
        exp_btn.pack(side="right", padx=20, pady=(0, 20))

        self.current = oop_code
        self.not_current = code

    def change_oop(self):

        if self.oop_code_switch.get() == 0:
            code = self.not_current
            oop_code = self.current
            self.current = code
            self.not_current = oop_code

        else:
            oop_code = self.not_current
            code = self.current
            self.current = oop_code
            self.not_current = code
        self.codeviewer.delete(1.0, "end")
        self.codeviewer._add_code(self.current.get_code(), "python")

    def escape_special_chars(self, text):
        escape_table = {
            "\n": "\\n",
            "\t": "\\t",
            "\"": "\\\"",
            "'": "\\'"
        }
        formatted_text = text
        for char, escape_seq in escape_table.items():
            formatted_text = formatted_text.replace(char, escape_seq)
        return formatted_text

    def loop_generate(self, d, parent, code, run=False):
        for x in list(d.keys()):
            if x.props == {}:
                code.add_line(f"{x.get_name()} = {x.get_class()}(master={parent})")
                if x.type == "FRAME":
                    code.add_line(f"{x.get_name()}.pack_propagate(False)")
            else:
                p = ""
                font = "font=CTkFont("
                for key in list(x.props.keys()):
                    if key == "image" and x.props["image"] != None:
                        if not run:
                            p += f'image=CTkImage(Image.open("Assets/{os.path.basename(x.props["image"].cget("dark_image").filename)}"), size=({x.props["image"].cget("size")[0]}, {x.props["image"].cget("size")[1]})), '
                        else:
                            p += f'image=CTkImage(Image.open("{x.props["image"].cget("dark_image").filename}"), size=({x.props["image"].cget("size")[0]}, {x.props["image"].cget("size")[1]})), '
                    elif key in ["font_family", "font_size", "font_weight", "font_slant", "font_underline",
                               "font_overstrike"]:
                        if type(x.props[key]) == str:

                            font += f'{key[5::]}="{x.props[key]}", '
                        else:
                            font += f'{key[5::]}={x.props[key]}, '
                    else:
                        if type(x.props[key]) == str:
                            k = self.escape_special_chars(x.props[key])
                            p += f'{key}="{k}", '
                        elif type(x.props[key]) == tuple:
                            if type(x.props[key][0]) == str and type(x.props[key][1]) == str:
                                p += f'{key}=("{x.props[key][0]}", "{x.props[key][1]}"), '
                            else:
                                p += f"{key}=({x.props[key][0]}, {x.props[key][1]}), "
                        else:
                            p += f"{key}={x.props[key]}, "

                font = font[0:-2] # Delete ', ' at last part
                font += ")"
                #print(font)
                if font != "font=CTkFon)": # Which means there is no change in font
                    p += font
                else:
                    p = p[0:-2]
                code.add_line(f"{x.get_name()} = {x.get_class()}(master={parent}, {p})")
                if x.type == "FRAME":
                    code.add_line(f"{x.get_name()}.pack_propagate(False)")
            if x.pack_options == {}:
                code.add_line(f"{x.get_name()}.pack()")
            else:
                p = ""
                for key in list(x.pack_options.keys()):
                    if type(x.pack_options[key]) == str:
                        p += f'{key}="{x.pack_options[key]}", '
                    elif type(x.pack_options[key]) == tuple:
                        if type(x.pack_options[key][0]) == str and type(x.pack_options[key][1]) == str:
                            p += f'{key}=("{x.pack_options[key][0]}", "{x.pack_options[key][1]}"), '
                        else:
                            p += f"{key}=({x.pack_options[key][0]}, {x.pack_options[key][1]}), "
                    else:
                        p += f"{key}={x.pack_options[key]}, "

                p = p[0:-2]  # Delete ', ' at last part
                code.add_line(f"{x.get_name()}.pack({p})")
            if d[x] != {}:
                #btn = CTkButton(self, text=x.type, command=lambda x=x: x.on_drag_start(None))

                self.loop_generate(d=d[x], parent=x.get_name(), code=code, run=run)

    def open_file(self):
        file = askdirectory()
        if file != "":
            self.file = [os.path.dirname(file), os.path.basename(file)]

            shutil.rmtree('temp')
            shutil.copytree(os.path.join(file, "Assets"), "temp")

            with open(os.path.join(file, f"{os.path.basename(file)}.json"), 'r') as openfile:
                d = json.load(openfile)
            d = d["MAIN-1"]

            self.r.props = d["parameters"]
            self.r._inner_id = d["ID"]
            for key in list(d["parameters"].keys()):
                if key == "width":
                    self.r.configure(width=d["parameters"]["width"])
                elif key == "height":
                    self.r.configure(height=d["parameters"]["height"])
                elif key == "fg_color":
                    self.r.configure(fg_color=d["parameters"]["fg_color"])

            d.pop("TYPE")
            d.pop("parameters")
            d.pop("pack_options")
            d.pop("ID")

            self.theme_manager = ThemeUtl(theme_dir=f"Themes", theme_name=d["theme"])
            self.theme = self.theme_manager.get_theme_by_name()
            self.properties.color_manager.colors = d["palette"]
            self.properties.color_manager.on_change_list = d["palette_on_change"]
            d.pop("theme")
            d.pop("palette")
            d.pop("palette_on_change")
            self.loop_open(d, self.r)

    def loop_open(self, d, parent, copy=False):
        # I could destroy every child in self.r but could not add new widgets after destroying the children.
        for x in list(d.keys()):
            y = d[x]["TYPE"]
            if y == "FRAME":
                w = Frame
            elif y == "BUTTON":
                w = Button
            elif y == "LABEL":
                w = Label
            elif y == "SWITCH":
                w = Switch
            elif y == "ENTRY":
                w = Entry
            elif y == "MAIN":
                w = Main
            elif y == "TEXTBOX":
                w = TextBox
            elif y == "PROGRESSBAR":
                w = ProgressBar
            elif y == "SEGMENTEDBUTTON":
                w = SegmentedButton
            elif y == "SLIDER":
                w = Slider
            elif y == "OPTIONMENU":
                w = OptionMenu
            elif y == "CHECKBOX":
                w = CheckBox
            elif y == "RADIOBUTTON":
                w = RadioButton
            elif y == "SCROLLBAR":
                w = Scrollbar
            elif y == "COMBOBOX":
                w = ComboBox
            else:
                raise ModuleNotFoundError(f"The Widget is not available. Perhaps the file is edited. The unknown widget was {x}")

            f = CTkFont()
            i = None
            d_copy = dict(d[x]["parameters"])
            for p in dict(d[x]["parameters"]):
                if p == "image":
                    path = d[x]["parameters"]["image"]["image"]
                    file_name = os.path.basename(path)
                    img = os.path.join("temp", file_name)
                    i = CTkImage(light_image=Image.open(img), dark_image=Image.open(img), size=(d[x]["parameters"]["image"]["size"][0], d[x]["parameters"]["image"]["size"][1]))
                    d[x]["parameters"]["image"] = i

                elif p == "font_family":
                    #print(d[x], p)
                    f.configure(family=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_family")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_size":
                    f.configure(size=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_size")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_weight":
                    f.configure(weight=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_weight")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_slant":
                    f.configure(slant=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_slant")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_underline":
                    f.configure(underline=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_underline")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_overstrike":
                    f.configure(overstrike=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_overstrike")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
            #print(w, parent.get_name(), d[x]["parameters"])
            if d[x]["parameters"] != {}:
                if "orientation" in list(d[x]["parameters"].keys()):
                    new_widget = w(master=parent, orientation=d[x]["parameters"]["orientation"], properties=self.r.properties)
                    g = dict(d)
                    g[x]["parameters"].pop("orientation")
                    self.apply_theme_to_widget(new_widget)
                    new_widget.configure(**g[x]["parameters"])
                else:
                    new_widget = w(master=parent, properties=self.r.properties)
                    self.apply_theme_to_widget(new_widget)
                    new_widget.configure(**d[x]["parameters"])

                try:
                    #print(d_copy)
                    new_widget.image = d_copy["image"]["image"]
                    img = d[x]["parameters"]["image"]
                    d_copy["image"] = img
                    new_widget.size = (d[x]["parameters"]["image"].cget("size")[0], d[x]["parameters"]["image"].cget("size")[1])
                    #print(d_copy)

                except KeyError as e:
                    pass

                new_widget.props = d_copy

            else:
                new_widget = w(master=parent, properties=self.r.properties)
                self.apply_theme_to_widget(new_widget)

            new_widget.num = self.total_num

            if not copy:
                new_widget.name = x
            else:
                new_widget.name = new_widget.type + str(new_widget.num + 1) + "_copy"

            self.total_num += 1

            self.get_parents(new_widget)
            self.add_to_dict(self.widgets, self._parents, new_widget)

            self._parents = []
            new_widget.pack(**d[x]["pack_options"])
            new_widget.pack_options = d[x]["pack_options"]
            #new_widget.configure(bg_color=parent.cget("fg_color"))
            if new_widget.__class__ == SegmentedButton:
                new_widget.configure(command=lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
            else:
                new_widget.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))

            # new_widget.bind("<Button-1>", new_widget.on_drag_start)
            new_widget.on_drag_start(None)
            if not copy:
                new_widget._inner_id = d[x]["ID"]
                self.id_mapped_widgets[new_widget._inner_id] = new_widget
            else:
                new_widget._inner_id = str(uuid.uuid4())
                self.id_mapped_widgets[new_widget._inner_id] = new_widget
                arr = self.properties.color_manager.get_all_changes(d[x]["ID"])
                for i in arr:
                    ar = self.properties.color_manager.on_change_list[i[0]]
                    ar.append([new_widget._inner_id, i[1][1], i[1][2]])
                    self.properties.color_manager.on_change_list[i[0]] = ar

            ic(new_widget._inner_id, new_widget.cget("fg_color"), d, x)
            self.hierarchy.delete_children()
            self.hierarchy.update_list(self.widgets, 5)
            # new_widget.place(x=x, y=y)
            if new_widget.__class__ != SegmentedButton:
                self.drag_manager.update_children(children=parent.winfo_children())
            d[x].pop("TYPE")
            d[x].pop("pack_options")
            d[x].pop("parameters")
            d[x].pop("ID")

            if d[x] != {}:
                self.loop_open(d[x], new_widget, copy=copy)

    def save(self, dir_, name):
        try:
            os.mkdir(path=os.path.join(dir_, name))
            os.mkdir(path=os.path.join(os.path.join(dir_, name), "Assets"))
            #shutil.copytree("temp", os.path.join(os.path.join(dir_, name), "Assets"))

            self.s = {self.r.get_name(): {}}
            self.loop_save(self.widgets, self.r.get_name(), self.s)
            self.s = self.s[self.r.get_name()]
            #print(self.s)
            self.s[self.r.get_name()]["theme"] = self.theme_manager.name
            self.s[self.r.get_name()]["palette_on_change"] = self.properties.color_manager.on_change_list
            self.s[self.r.get_name()]["palette"] = self.properties.color_manager.colors
            self.file = [dir_, name]
            json_object = json.dumps(self.s, indent=4)
            with open(os.path.join(os.path.join(dir_, name), f"{name}.json"), "w") as outfile:
                outfile.write(json_object)
        except FileExistsError as e:
            self.file = ""
            tkinter.messagebox.showerror("Error", f"File Exists: {os.path.join(dir_, name)}")
        #os.mkdir(path=os.path.join(os.path.join(dir_, name), "Assets"))
    def set_file(self, dir_, name):
        self.file = [dir_, name]
        self.save(dir_, name)

    def save_file(self):

        if self.file == "":
            f = SaveFileDialog(callback=self.set_file)

        if self.file != "":
            shutil.rmtree(os.path.join(os.path.join(self.file[0], self.file[1]), "Assets"))
            #shutil.copytree("temp", os.path.join(os.path.join(self.file[0], self.file[1]), "Assets"))
            os.mkdir(path=os.path.join(os.path.join(self.file[0], self.file[1]), "Assets"))
            self.s = {self.r.get_name(): {}}
            self.loop_save(self.widgets, self.r.get_name(), self.s)
            self.s = self.s[self.r.get_name()]
            self.s[self.r.get_name()]["theme"] = self.theme_manager.name
            self.s[self.r.get_name()]["palette_on_change"] = self.properties.color_manager.on_change_list
            self.s[self.r.get_name()]["palette"] = self.properties.color_manager.colors
            json_object = json.dumps(self.s, indent=4)
            with open(os.path.join(os.path.join(self.file[0], self.file[1]), f"{self.file[1]}.json"), "w") as outfile:
                outfile.write(json_object)

    def saveas_file(self):
        f = SaveFileDialog(callback=self.save)

    def loop_save(self, d, parent, code):
        #print(d)
        for x in list(d.keys()):
            props = dict(x.props)
            if "image" in list(props.keys()):
                #print(x.get_name(), x.props)
                img = os.path.basename(x.props["image"].cget("dark_image").filename)
                path = os.path.join("Assets", img)
                #ic(x.props["image"].cget("dark_image").filename, self.file)
                shutil.copy2(x.props["image"].cget("dark_image").filename, f"{self.file[0]}/{self.file[1]}/Assets")
                props["image"] = {"image": path, "size": [x.size[0], x.size[1]]}

            code[parent][x.get_name()] = {"TYPE": x.type, "parameters": props, "pack_options": x.pack_options, "ID": x._inner_id}

            if d[x] != {}:
                self.loop_save(d[x], x.get_name(), code[parent])

        #print(code)

    def loop_generate_oop(self, d, parent, code):

        for x in list(d.keys()):
            if x.props == {}:

                code.add_line(f"self.{x.get_name()} = {x.get_class()}(master={parent})")
                if x.type == "FRAME":
                    code.add_line(f"self.{x.get_name()}.pack_propagate(False)")
            else:


                p = ""
                font = "font=CTkFont("
                for key in list(x.props.keys()):
                    if key == "image" and x.props["image"] != None:

                        p += f'image=CTkImage(Image.open("Assets/{os.path.basename(x.props["image"].cget("dark_image").filename)}"), size=({x.props["image"].cget("size")[0]}, {x.props["image"].cget("size")[1]})), '
                    elif key in ["font_family", "font_size", "font_weight", "font_slant", "font_underline",
                               "font_overstrike"]:
                        if type(x.props[key]) == str:

                            font += f'{key[5::]}="{x.props[key]}", '
                        else:
                            font += f'{key[5::]}={x.props[key]}, '
                    else:
                        if type(x.props[key]) == str:
                            k = self.escape_special_chars(x.props[key])
                            p += f'{key}="{k}", '
                        elif type(x.props[key]) == tuple:
                            if type(x.props[key][0]) == str and type(x.props[key][1]) == str:
                                p += f'{key}=("{x.props[key][0]}", "{x.props[key][1]}"), '
                            else:
                                p += f"{key}=({x.props[key][0]}, {x.props[key][1]}), "
                        else:
                            p += f"{key}={x.props[key]}, "

                font = font[0:-2] # Delete ', ' at last part
                font += ")"
                #print(font)
                if font != "font=CTkFon)": # Which means there is no change in font
                    p += font
                else:
                    p = p[0:-2]
                code.add_line(f"self.{x.get_name()} = {x.get_class()}(master={parent}, {p})")
                if x.type == "FRAME":
                    code.add_line(f"self.{x.get_name()}.pack_propagate(False)")
            if x.pack_options == {}:
                code.add_line(f"self.{x.get_name()}.pack()")
            else:
                p = ""
                for key in list(x.pack_options.keys()):
                    if type(x.pack_options[key]) == str:
                        p += f'{key}="{x.pack_options[key]}", '
                    elif type(x.pack_options[key]) == tuple:
                        if type(x.pack_options[key][0]) == str and type(x.pack_options[key][1]) == str:
                            p += f'{key}=("{x.pack_options[key][0]}", "{x.pack_options[key][1]}"), '
                        else:
                            p += f"{key}=({x.pack_options[key][0]}, {x.pack_options[key][1]}), "
                    else:
                        p += f"{key}={x.pack_options[key]}, "

                p = p[0:-2]  # Delete ', ' at last part
                code.add_line(f"self.{x.get_name()}.pack({p})")
            if d[x] != {}:
                #btn = CTkButton(self, text=x.type, command=lambda x=x: x.on_drag_start(None))

                self.loop_generate_oop(d=d[x], parent="self." + x.get_name(), code=code)


    def get_parents(self, widget):
        if widget == self.r:
            self._parents.reverse()
            pass
        else:
            if type(widget) != ScrollableFrame:
                self._parents.append(widget.master)
                self.get_parents(widget.master)
            else:
                self._parents.append(widget.master.master.master)
                self.get_parents(widget.master.master.master)



    def redraw(self, d):
        for x in list(d.keys()):

            if d[x] != {}:
                #btn = CTkButton(self, text=x.type, command=lambda x=x: x.on_drag_start(None))
                if x.pack_options == {}:
                    x.pack()
                else:
                    x.pack(**x.pack_options)
                self.redraw(d[x])
            else:
                if x.pack_options == {}:
                    x.pack()
                else:
                    x.pack(**x.pack_options)

    def destroy_children(self):
        for widget in self.r.winfo_children():
            widget.destroy()

    def add_to_dict(self, my_dict, key_list, value):
        current_dict = my_dict
        for key in key_list[:-1]:  # Iterate through all keys except the last one

            current_dict = current_dict[key]  # Move to the nested dictionary

        # If the current dict is not empty (There something already there)
        if current_dict[key_list[-1]] != {}:
            current_dict[key_list[-1]][value] = {}
            value.order = len(current_dict[key_list[-1]])

        # If the current dict is empty This is the first widget
        else:
            current_dict[key_list[-1]] = {value: {}}
            value.order = 1


    def get_first_degree_parent(self, my_dict, key_list):

        current_dict = my_dict
        for key in key_list[:-1]:  # Iterate through all keys except the last one

            current_dict = current_dict[key]  # Move to the nested dictionary

        return current_dict[key_list[-1]]

    def simple_order_dict(self, data_dict):
        """
        This function orders a dictionary by the 'order' variable of its class keys.

        Args:
            data_dict: The dictionary to be ordered.

        Returns:
            A new dictionary ordered by the 'order' attribute of the class keys.
        """
        # Use sorted with a lambda function directly accessing the order attribute
        return dict(sorted(data_dict.items(), key=lambda item: getattr(item[0], 'order', 0)))

    def loop_order_sort(self, d):
        """
        This function recursively sorts a dictionary based on class key order
        and sorts nested dictionaries (if possible).

        Args:
            d: The dictionary to be sorted.

        Returns:
            The modified dictionary with sorted elements.
        """

        new_d = self.simple_order_dict(d)


        for key in new_d:
            value = new_d[key]

            if value != {}:
                # Recursively sort nested dictionaries
                new_d[key] = self.loop_order_sort(value)

        return new_d

    def add_widget(self, w, properties, widget, x=0, y=0):

        new_widget = w(master=widget.master, **properties)
        new_widget.num = self.total_num
        new_widget.name = new_widget.type + str(new_widget.num)
        self.apply_theme_to_widget(new_widget)
        if new_widget.__class__ == Slider or new_widget.__class__ == Scrollbar:
            new_widget.props["orientation"] = properties["orientation"]

        self.total_num += 1
        self.get_parents(new_widget)
        self.add_to_dict(self.widgets, self._parents, new_widget)
        self.id_mapped_widgets[new_widget._inner_id] = new_widget
        self._parents = []
        new_widget.configure(bg_color="transparent")
        new_widget.pack(padx=(0, 0), pady=(0, 0))

        if new_widget.__class__ == SegmentedButton:
            new_widget.configure(command=lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
        else:
            new_widget.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))



        #new_widget.bind("<Button-1>", new_widget.on_drag_start)

        self.hierarchy.delete_children()
        self.hierarchy.update_list(self.widgets, 5)
        #new_widget.place(x=x, y=y)
        if new_widget.__class__ != SegmentedButton:
            self.drag_manager.update_children(children=widget.master.winfo_children())

    def delete_from_dict(self, my_dict, key_list, value):
        current_dict = my_dict
        for key in key_list[:-1]:  # Iterate through all keys except the last one

            current_dict = current_dict[key]  # Move to the nested dictionary

        # If the current dict is not empty (There something already there)
        if current_dict[key_list[-1]] != {}:
            current_dict[key_list[-1]].pop(value)
    def show_palette(self, properties):
        print(self.id_mapped_widgets, properties.color_manager.on_change_list)
        palette = PaletteEditor(color_manager=properties)




class WidgetButton(CTkButton):
    def __init__(self, on_drag, **kwargs):
        self.on_drag = on_drag
        super().__init__(**kwargs)


class Hierarchy(CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_selection = None
        self.widget = None
        self.main = None
        self.mainwindow = None
        self.btns = []

    def set_current_selection(self, x):
        if x != self.main.r:
            for b in self.btns:
                b.configure(state="normal")
        else:

            for b in self.btns:
                b.configure(state="disabled")

        #self.current_selection = btn
        self.widget = x

        for child in self.winfo_children():

            if child.cget("text") != self.widget.get_name():
                child.configure(fg_color="#113D5F")
            else:
                self.current_selection = child
                child.configure(fg_color="#1F6AA5")

    def update_text(self, old_name, new_text):

        for child in self.winfo_children():
            if child.widget == self.widget and child.cget("text") == old_name:
                child.configure(text=new_text)

    def delete_widget(self):

        #self.widget.destroy()
        self.main._parents = []
        self.main.get_parents(self.widget)
        self.main.delete_from_dict(self.main.widgets, self.main._parents, self.widget)
        self.main._parents = []

        self.widget.destroy()
        self.widget = None
        self.current_selection = None
        self.delete_children()
        self.update_list(self.main.widgets, 5)
        for btn in self.btns:
            btn.configure(state="disabled")


    def move_up(self):
        if self.current_selection != None:
            self.main.get_parents(self.widget)
            parents = self.main._parents
            siblings = self.main.get_first_degree_parent(self.main.widgets, parents)
            selection_order = self.widget.order
            sib = None
            for sibling in siblings:
                if sibling.order + 1 == selection_order:
                    sib = sibling
                    break
            if sib is not None:
                sib.order = selection_order
                self.widget.order = sib.order - 1
                self.widget.pack(**self.widget.pack_options, before=sib)
                self.main.widgets = self.main.loop_order_sort(self.main.widgets)

                self.delete_children()
                self.update_list(self.main.widgets, 5)

            self.main._parents = []
            self.current_selection = None
            self.widget = None
            for btn in self.btns:
                btn.configure(state="disabled")
            #print(self.main.widgets)
    def move_down(self):
        if self.current_selection != None:
            self.main.get_parents(self.widget)
            parents = self.main._parents
            siblings = self.main.get_first_degree_parent(self.main.widgets, parents)
            selection_order = self.widget.order
            sib = None
            for sibling in siblings:
                if sibling.order - 1 == selection_order:
                    sib = sibling
                    break
            if sib is not None:
                sib.order = selection_order
                self.widget.order = sib.order + 1
                self.widget.pack(**self.widget.pack_options, after=sib)
                self.main.widgets = self.main.loop_order_sort(self.main.widgets)

                self.delete_children()
                self.update_list(self.main.widgets, 5)

            self.main._parents = []
            self.current_selection = None
            self.widget = None
            for btn in self.btns:
                btn.configure(state="disabled")
            #print(self.main.widgets)

    def update_list(self, d, pad):
        self.current_selection = None
        self.widget = None
        for x in list(d.keys()):
            if d[x] != {}:
                btn = CTkButton(self, text=x.get_name(), fg_color="#113D5F")
                #x.bind("<Button-1>", lambda e, x=x, btn=btn: (x.on_drag_start(None), self.set_current_selection(btn, x)))
                btn.configure(command=lambda x=x: (x.on_drag_start(None), self.set_current_selection(x)))
                btn.widget = x
                btn.pack(fill="x", padx=(pad, 5), pady=2.5)
                self.update_list(d[x], pad+20)
            else:

                btn = CTkButton(self, text=x.get_name(), fg_color="#113D5F")
                #x.bind("<Button-1>", lambda e, x=x, btn=btn: (x.on_drag_start(None), self.set_current_selection(btn, x)))
                btn.configure(command=lambda x=x: (x.on_drag_start(None), self.set_current_selection(x)))
                btn.widget = x
                btn.pack(fill="x", padx=(pad, 5), pady=2.5)


    def duplicate_widget(self):
        # This method is not efficient
        #ic(self.main.widgets)
        self.s = {self.widget.get_name(): {}}
        self.main._parents = []
        self.main.get_parents(self.widget)

        #ic(self.main._parents)
        d = self.main.widgets.copy()
        for key in self.main._parents:
            d = d[key]

        val = d[self.widget]
        d = {self.widget: val}
        #ic(self.main.widgets)

        #ic(d)
        self.main._parents = []
        self.main.loop_save(d, self.widget.get_name(), self.s)
        self.s = self.s[self.widget.get_name()]
        #ic(self.main.widgets)
        self.main.loop_open(self.s, self.widget.master, copy=True)
        #self.s[self.r.get_name()]["theme"] = self.theme_manager.name
        #ic(self.main.widgets)


    def delete_children(self):
        for widget in self.winfo_children():
            widget.destroy()

class PaletteEditor(CTkToplevel):
    def __init__(self, *args, color_manager, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x500")
        self.color = "#FFFFFF"

        self.current_selection = [None, None]
        self.clickables = []
        self.color_manager = color_manager.color_manager
        self.scrl = CTkScrollableFrame(self)
        self.scrl.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.frame2 = CTkFrame(self)
        self.frame2.pack(fill="x", padx=10, pady=(10, 5))

        self.name_entry = CTkEntry(self.frame2, placeholder_text="Enter Name")
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=5)

        self.add_btn = CTkButton(self.frame2, text="Add", width=50, command=self.add)
        self.add_btn.pack(side="left", padx=10)

        self.fr = CTkFrame(self)
        self.fr.pack(padx=10, pady=(5, 10), fill="x")

        self.c = CTkButton(self.fr, width=100, height=100, text="", fg_color=self.color, hover=False, command=self.get_color)
        self.c.pack(side="left")



        self.hex = CTkLabel(self.fr, text=f"HEX: {self.color}", anchor="w")
        self.hex.pack(fill="x", padx=10, pady=5, expand=True)


        self.rgb = CTkLabel(self.fr, text=f"RGB: {self.hex_to_rgb(self.color)}", anchor="w")
        self.rgb.pack(fill="x", padx=10, pady=(0, 5), expand=True)

        self.change_btn = CTkButton(self.fr, text=f"Change", command=self.use)
        self.change_btn.pack(fill="x", padx=10, pady=(0, 10), expand=True)

        for x in list(self.color_manager.colors.keys()):
            self.add_color_option(x, self.color_manager.get_color(x))

    def add(self):
        self.color_manager.add_color(name=self.name_entry.get(), color=self.c.cget("fg_color"))
        self.add_color_option(self.name_entry.get(), self.color_manager.get_color(self.name_entry.get()))
        self.name_entry.delete(0, "end")

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def select(self, name, val):
        self.current_selection = [name, val]
        self.c.configure(fg_color=self.color_manager.get_color(name))
        self.hex.configure(text=f"HEX: {self.color_manager.get_color(name)}")
        self.rgb.configure(text=f"RGB: {self.hex_to_rgb(self.color_manager.get_color(name))}")

    def add_color_option(self, name, val):
        c = CTkFrame(self.scrl, height=100)
        c.pack(fill="x", pady=10)

        clr = CTkFrame(c, width=75, height=75, fg_color=val)
        clr.pack(side="left", padx=10)

        fr = CTkFrame(c)
        fr.pack(side="left", fill="both", expand=True)

        lbl = CTkLabel(fr, text=name, anchor="w", font=CTkFont(size=17))
        lbl.pack(fill="x", expand=True, padx=10, pady=10)

        lbl2 = CTkLabel(fr, text=val, anchor="w")
        lbl2.pack(fill="x", expand=True, padx=10, pady=(0, 10))

        btn = CTkButton(c, text="X",fg_color="#D0255E", hover_color="#AE1E4F", width=50, height=50)
        btn.pack(side="left", padx=10)


        for x in [c, clr, fr, lbl, lbl2]:
            x.bind("<Button-1>", lambda e, name=name, val=val: (self.select(name, val), self.change_selection([fr, c])))
        btn.configure(command=lambda: (self.color_manager.delete_color(name), c.destroy()))
        self.select(name, val)
        self.change_selection([fr, c])
        self.clickables.append([fr, c])
    def get_color(self):
        c = askcolor(initialcolor=self.c.cget("fg_color"))
        if c != (None, None):
            self.c.configure(fg_color=c[1])

    def use(self):
        if self.command != None:
            #self.command(self.c.cget("fg_color"), self.current_selection)
            self.color_manager.edit(name=self.current_selection[0], val=self.c.cget("fg_color"))
            self.destroy()



    def change_selection(self, clr):
        for x in self.clickables:
            for y in x:
                y.configure(fg_color="transparent")
        for x in clr:
            x.configure(fg_color="#1F6AA5")

    def rgb2hex(self, c):
        return '#%02x%02x%02x' % c
class App(CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry("1900x1000+10+0")
        self.title("Custom Tkinter Builder")
        self.app_theme = "blue"
        self.canvas_theme = "green"

        self.tool_bar = CTkFrame(self, height=40)
        self.tool_bar.pack(side="top", fill="x", padx=10, pady=(10, 0))

        self.save_btn = CTkButton(self.tool_bar, text="Save")
        self.save_btn.pack(side="left", padx=5, pady=5)

        self.saveas_btn = CTkButton(self.tool_bar, text="Save As")
        self.saveas_btn.pack(side="left", padx=5, pady=5)

        self.open_btn = CTkButton(self.tool_bar, text="Open")
        self.open_btn.pack(side="left", padx=5, pady=5)

        self.run_code_btn = CTkButton(self.tool_bar, text="Run Code")
        self.run_code_btn.pack(side="left", padx=5, pady=5)

        self.export_code_btn = CTkButton(self.tool_bar, text="Export Code")
        self.export_code_btn.pack(side="left", padx=5, pady=5)

        self.palette_btn = CTkButton(self.tool_bar, text="Edit Palette")
        self.palette_btn.pack(side="left", padx=5, pady=5)

        self.appearance_mode_switch = CTkSwitch(self.tool_bar, text="Dark Mode")
        self.appearance_mode_switch.pack(side="left", padx=5, pady=5)
        self.appearance_mode_switch.toggle()
        self.appearance_mode_switch.configure(command=lambda: self.main.change_appearance_mode(self.appearance_mode_switch.get()))

        self.widget_panel = CTkScrollableFrame(self, width=350)
        self.widget_panel.pack(side=LEFT, padx=10, pady=10, fill="y")

        self.add_frame_btn = WidgetButton(master=self.widget_panel, text="Frame", height=50,
                                          on_drag=lambda x, y, widget: self.main.add_widget(Frame, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_frame_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_button_btn = WidgetButton(master=self.widget_panel, text="Button", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Button, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_button_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_label_btn = WidgetButton(master=self.widget_panel, text="Label", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Label, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_label_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_entry_btn = WidgetButton(master=self.widget_panel, text="Entry", height=50,
                                          on_drag=lambda x, y, widget: self.main.add_widget(Entry, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_entry_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_switch_btn = WidgetButton(master=self.widget_panel, text="Switch", height=50,
                                          on_drag=lambda x, y, widget: self.main.add_widget(Switch, properties={
                                              "properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_switch_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_textbox_btn = WidgetButton(master=self.widget_panel, text="TextBox", height=50,
                                          on_drag=lambda x, y, widget: self.main.add_widget(TextBox, properties={
                                              "properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_textbox_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_progressbar_btn = WidgetButton(master=self.widget_panel, text="Progress Bar", height=50,
                                          on_drag=lambda x, y, widget: self.main.add_widget(ProgressBar, properties={
                                              "properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_progressbar_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_segmentedbutton_btn = WidgetButton(master=self.widget_panel, text="Segmented Button", height=50,
                                               on_drag=lambda x, y, widget: self.main.add_widget(SegmentedButton,
                                                                                                 properties={
                                                                                                     "properties": self.properties_panel},
                                                                                                 x=x, y=y,
                                                                                                 widget=widget))
        self.add_segmentedbutton_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_horizontalslider_btn = WidgetButton(master=self.widget_panel, text="Horizontal Slider", height=50,
                                               on_drag=lambda x, y, widget: self.main.add_widget(Slider,
                                                                                                 properties={
                                                                                                     "properties": self.properties_panel, "orientation": "horizontal"},
                                                                                                 x=x, y=y,
                                                                                                 widget=widget))
        self.add_horizontalslider_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_verticalslider_btn = WidgetButton(master=self.widget_panel, text="Vertical Slider", height=50,
                                           on_drag=lambda x, y, widget: self.main.add_widget(Slider,
                                                                                             properties={
                                                                                                 "properties": self.properties_panel, "orientation": "vertical"},
                                                                                             x=x, y=y,
                                                                                             widget=widget))
        self.add_verticalslider_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_optionmenu_btn = WidgetButton(master=self.widget_panel, text="Option Menu", height=50,
                                               on_drag=lambda x, y, widget: self.main.add_widget(OptionMenu,
                                                                                                 properties={
                                                                                                     "properties": self.properties_panel},
                                                                                                 x=x, y=y,
                                                                                                 widget=widget))
        self.add_optionmenu_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_checkbox_btn = WidgetButton(master=self.widget_panel, text="Check Box", height=50,
                                               on_drag=lambda x, y, widget: self.main.add_widget(CheckBox,
                                                                                                 properties={
                                                                                                     "properties": self.properties_panel},
                                                                                                 x=x, y=y,
                                                                                                 widget=widget))
        self.add_checkbox_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_radiobutton_btn = WidgetButton(master=self.widget_panel, text="Radio Button", height=50,
                                             on_drag=lambda x, y, widget: self.main.add_widget(RadioButton,
                                                                                               properties={
                                                                                                   "properties": self.properties_panel},
                                                                                               x=x, y=y,
                                                                                               widget=widget))
        self.add_radiobutton_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_horizontalscrollbar_btn = WidgetButton(master=self.widget_panel, text="Horizontal Scrollbar", height=50,
                                                on_drag=lambda x, y, widget: self.main.add_widget(Scrollbar,
                                                                                                  properties={
                                                                                                      "properties": self.properties_panel, "orientation": "horizontal"},
                                                                                                  x=x, y=y,
                                                                                                  widget=widget))
        self.add_horizontalscrollbar_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_verticalscrollbar_btn = WidgetButton(master=self.widget_panel, text="Vertical Scrollbar", height=50,
                                              on_drag=lambda x, y, widget: self.main.add_widget(Scrollbar,
                                                                                                properties={
                                                                                                    "properties": self.properties_panel, "orientation": "vertical"},
                                                                                                x=x, y=y,
                                                                                                widget=widget))
        self.add_verticalscrollbar_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.add_combobox_btn = WidgetButton(master=self.widget_panel, text="Combo Box", height=50,
                                                      on_drag=lambda x, y, widget: self.main.add_widget(ComboBox,
                                                                                                        properties={
                                                                                                            "properties": self.properties_panel},
                                                                                                        x=x, y=y,
                                                                                                        widget=widget))
        self.add_combobox_btn.pack(padx=10, pady=(10, 0), fill="x")

        self.main_window_panel = CTkFrame(self)
        self.main_window_panel.pack(side=LEFT, pady=10, fill="both", expand=True)

        self.temp = CTkFrame(self.main_window_panel)
        self.temp.pack(fill="both", expand=True)

        self.main_window = Main(self.temp, properties=None, width=500, height=500, bg_color="transparent")
        self.main_window.pack_propagate(False)
        self.main_window.place(anchor="center", relx=0.5, rely=0.5)
        self.main_window.type = "MAIN"
        self.main_window.num = -1
        self.main_window.name = self.main_window.type + str(self.main_window.num)

        self.drag_manager = DragManager([self.add_frame_btn, self.add_button_btn, self.add_entry_btn, self.add_label_btn, self.add_switch_btn, self.add_textbox_btn, self.add_progressbar_btn, self.add_segmentedbutton_btn, self.add_horizontalslider_btn, self.add_verticalslider_btn,self.add_optionmenu_btn, self.add_checkbox_btn, self.add_radiobutton_btn, self.add_horizontalscrollbar_btn, self.add_verticalscrollbar_btn, self.add_combobox_btn], self.main_window, self)

        self.main = MainWindow(self.main_window, self.canvas_theme)
        self.main.drag_manager = self.drag_manager
        self.main_window.configure(fg_color=self.main.theme["CTk"]["fg_color"], bg_color=self.main_window.master.cget("fg_color")[1])
        self.container = CTkFrame(self, width=350)
        self.container.pack(side=LEFT, padx=10, pady=10, fill="y")
        self.container.pack_propagate(False)

        self.hierarchy = Hierarchy(self.container, height=350)
        self.hierarchy.pack(fill="both")
        self.main.hierarchy = self.hierarchy
        self.hierarchy.main = self.main
        self.hierarchy.mainwindow = self.main_window
        self.hierarchy_tools_container = CTkFrame(self.container, height=40)
        self.hierarchy_tools_container.pack(fill="x", pady=(0, 10))

        # Need to change those unicode with icons
        self.move_top_btn = CTkButton(self.hierarchy_tools_container, text="south", font=CTkFont(family="MaterialIconsOutlined-Regular", size=22), width=30, height=30, command=self.hierarchy.move_up)
        self.move_top_btn.pack(side="left", padx=5)

        self.move_down_btn = CTkButton(self.hierarchy_tools_container, text="north", font=CTkFont(family="MaterialIconsOutlined-Regular", size=22), width=30, height=30, command=self.hierarchy.move_down)
        self.move_down_btn.pack(side="left", padx=5)

        self.delete_btn = CTkButton(self.hierarchy_tools_container, text="delete", font=CTkFont(family="MaterialIconsOutlined-Regular", size=22), width=30, height=30, command=self.hierarchy.delete_widget)
        self.delete_btn.pack(side="left", padx=5)

        self.duplicate_btn = CTkButton(self.hierarchy_tools_container, text="content_copy",
                                    font=CTkFont(family="MaterialIconsOutlined-Regular", size=22), width=30, height=30,
                                    command=self.hierarchy.duplicate_widget)
        self.duplicate_btn.pack(side="left", padx=5)

        self.hierarchy.btns = [self.move_top_btn, self.move_down_btn, self.delete_btn, self.duplicate_btn]
        for btn in self.hierarchy.btns:
            btn.configure(state="disabled")
        self.properties_panel = PropertiesManager(self.container, main=self.main)
        self.main.properties = self.properties_panel
        self.properties_panel.pack(fill="both", expand=True)
        self.main_window.properties = self.properties_panel
        self.main_window.bind("<Button-1>", lambda e, nw=self.main_window: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
        self.run_code_btn.configure(command=self.main.run_code)
        self.export_code_btn.configure(command=self.main.export_code)
        self.palette_btn.configure(command=lambda: self.main.show_palette(self.properties_panel))

        self.save_btn.configure(command=self.main.save_file)
        self.saveas_btn.configure(command=self.main.saveas_file)

        self.open_btn.configure(command=self.main.open_file)
        self.hierarchy.delete_children()
        self.hierarchy.update_list(self.main.widgets, 5)

        self.main.apply_theme_to_widget(self.main_window)

# Need to create a custom theme with corner_radius - 3 (Will look more elegant and professional)
set_default_color_theme("blue")
#set_appearance_mode("dark")
shutil.rmtree("temp")
os.mkdir("temp")
app = App()
app.mainloop()