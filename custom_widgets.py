import tkinter as tk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None, fg="white", font=("Segoe UI", 10, "bold")):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
                          relief="flat", highlightthickness=0, bg=parent['bg'])
        self.command = command
        self.color = color
        
        if cornerradius > 0.5*width: cornerradius = 0.5*width
        if cornerradius > 0.5*height: cornerradius = 0.5*height

        rad = cornerradius
        self.config(width=width, height=height)
        
        self.rect = self.create_rounded_rect(0, 0, width, height, rad, fill=color, outline=color)
        self.text = self.create_text(width/2, height/2, text=text, fill=fg, font=font)
        
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.move(self.text, 1, 1)

    def _on_release(self, event):
        self.move(self.text, -1, -1)
        if self.command: self.command()

    def _on_enter(self, event):
        self.itemconfig(self.rect, fill=self._adjust_color(self.color, -20))

    def _on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)

    def _adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        rgb = [max(0, min(255, c + amount)) for c in rgb]
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def config_state(self, state):
        if state == tk.DISABLED:
            self.itemconfig(self.rect, fill="#bdc3c7", outline="#bdc3c7")
            self.unbind("<ButtonPress-1>")
        else:
            self.itemconfig(self.rect, fill=self.color, outline=self.color)
            self.bind("<ButtonPress-1>", self._on_press)
