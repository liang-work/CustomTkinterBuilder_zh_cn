from customtkinter import CTkTextbox
from PackArgs import PackArgs
from widgets import BaseWidgetClass
class TextBox(CTkTextbox, PackArgs, BaseWidgetClass):
    def __init__(self, *args, properties, **kwargs):
        super(TextBox, self).__init__(*args, **kwargs)
        BaseWidgetClass.__init__(self)
        self.type = "TEXTBOX"
        self.properties = properties
        self.pack_options = {}
        self.pack_propagate(False)
        #self.configure(bg_color=self.master.cget("fg_color"))
        self.order = 0
        self.num = None
        self.name = None

        #self.bind("<B1-Motion>", self.on_drag_motion)
        self.props = {}
        self.bind_mouse(properties)

    def __repr__(self):

        return f"{self.type}_{str(self.order)}"

    def get_class(self):
        return "CTkTextbox"

    def get_name(self):
        return self.name.replace(" ", "_")

    def save(self, func, key, val, arg):
        self.props[key] = val
        func(arg)

    def configure(self, require_redraw=False, **kwargs):
        print(kwargs)
        super().configure(require_redraw, **kwargs)


    def _bool_change(self, val):
        if val == "True":
            return True
        elif val == "False":
            return False

    def change_name(self, name):
        self.name = name

    def on_drag_start(self, event):
        #self._drag_start_x = event.x
        #self._drag_start_y = event.y
        self.properties.destroy_children()
        #self.properties.add_seperator("Properties")
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "ID", "SINGLELINE_TEXT", "id", {"val": self.name, "callback": lambda val: (self.properties.main.hierarchy.update_text(self.name, val), self.change_name(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Width", "SPINBOX", "Width", {"to": 500, "from": 0, "val": int(self.cget("width")), "callback": lambda val: self.save(lambda val: self.configure(width=val), "width", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Height", "SPINBOX", "Height", {"to": 500, "from": 0, "val": int(self.cget("height")), "callback": lambda val: self.save(lambda val: self.configure(height=val), "height", int(val), int(val))})

        # Saw it in the documentation but it's not a supported argument
        # self.properties.add_option(self.properties.STYLES, "Activate Scrollbars", "COMBO", "activate_scrollbars", {"vals": ["True", "False"], "default": str(bool(self.cget("activate_scrollbars"))), "callback": lambda val: self.save(lambda val: self.configure(activate_scrollbars=val), "activate_scrollbars", self._bool_change(val), self._bool_change(val))})
        # self.properties.add_option(self.properties.STYLES, "Wrap", "COMBO", "wrap", {"vals": ["char", "word", "none"], "default": self.cget("wrap"), "callback": lambda val: self.save(lambda val: self.configure(wrap=val), "wrap", val, val)})
        # self.properties.add_option(self.properties.STYLES, "State", "COMBO", "state", {"vals": ["normal", "disabled"], "default": self.cget("state"), "callback": lambda val: self.save(lambda val: self.configure(state=val), "state", val, val)})

        # self.cget() doesn't support this. Why????
        # self.properties.add_option(self.properties.STYLES, "Scrollbar Button Color", "COLOR_COMBO", "scrollbar_button_color", {"color": self.cget("scrollbar_button_color"), "key": "scrollbar_button_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(scrollbar_button_color=val), "scrollbar_button_color", val, val)})
        # self.properties.add_option(self.properties.STYLES, "Scrollbar Button Hover Color", "COLOR_COMBO", "scrollbar_button_hover_color", {"color": self.cget("scrollbar_button_hover_color"), "key": "scrollbar_button_hover_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(scrollbar_button_hover_color=val), "scrollbar_button_hover_color", val, val)})


        self.properties.add_option(self.properties.STYLES, "Font Family", "FONT_FAMILY", "font_family", {"key": "font_family", "default": self.cget("font").cget("family"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(family=val), "font_family", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Size", "SPINBOX", "font_size", {"to": 500, "from": -500, "val": self.cget("font").cget("size"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(size=int(val)), "font_size", int(val), int(val))})
        self.properties.add_option(self.properties.STYLES, "Font Weight", "COMBO", "font_weight", {"vals": ["bold", "normal"], "default": self.cget("font").cget("weight"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(weight=val), "font_weight", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Slant", "COMBO", "font_slant", {"vals": ["italic", "roman"], "default": self.cget("font").cget("slant"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(slant=val), "font_slant", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Underline", "COMBO", "font_underline", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("underline"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(underline=val), "font_underline", self._bool_change(val), self._bool_change(val))})
        self.properties.add_option(self.properties.STYLES, "Font Overstrike", "COMBO", "font_overstrike", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("overstrike"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(overstrike=val), "font_overstrike", self._bool_change(val), self._bool_change(val))})

        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Corner Radius", "SPINBOX", "Corner Radius", {"to": 100, "from": 0, "val": self.cget("corner_radius"), "callback": lambda val: self.save(lambda val: self.configure(corner_radius=val), "corner_radius", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Border Width", "SPINBOX", "Border Width", {"to": 100, "from": 0, "val": self.cget("border_width"), "callback": lambda val: self.save(lambda val: self.configure(border_width=val), "border_width", int(val), int(val))})
        self.properties.add_option(self.properties.STYLES, "FG Color", "COLOR_COMBO", "fg_color", {"color": self.cget("fg_color"), "key": "fg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(fg_color=val), "fg_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "BG Color", "COLOR_COMBO", "bg_color", {"color": self.cget("bg_color"), "key": "bg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(bg_color=val), "bg_color", val, val)})

        self.properties.add_option(self.properties.STYLES, "Border Color", "COLOR_COMBO", "border_color", {"color": self.cget("border_color"), "key": "border_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(border_color=val), "border_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Text Color", "COLOR_COMBO", "text_color", {"color": self.cget("text_color"), "key": "text_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(text_color=val), "text_color", val, val)})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Border Spacing", "SPINBOX", "border_spacing", {"to": 100, "from": 0, "val": self.cget("border_spacing"), "callback": lambda val: self.save(lambda val: self.configure(border_spacing=val), "border_spacing", int(val), int(val))})



        self.default()
        # self.on_drag_motion(event)  # Some awkward problem


    def on_drag_motion(self, event):
        #x = self.winfo_x() - self._drag_start_x + event.x
        #y = self.winfo_y() - self._drag_start_y + event.y
        #self.properties.update_options("X", "SPINBOX", {"val": int(x)})
        #self.properties.update_options("Y", "SPINBOX", {"val": int(y)})

        pass
        #self.properties.update_options("Width", "SPINBOX", {"val": int(self.cget("width"))})
        #self.properties.update_options("Height", "SPINBOX", {"val": int(self.cget("height"))})
        #self.properties.update_options("Text", "TEXT", {"val": self.cget("text")})
        #self.properties.update_options("Corner Radius", "SPINBOX", {"val": self.cget("corner_radius")})
        #self.properties.update_options("Border Width", "SPINBOX", {"val": self.cget("border_width")})

        #self.place(x=x, y=y)