import tkinter as tk
from tkinter import ttk, messagebox
import convert, ops

COLORS = {
    "almond": "#F1DAC4",  # background base
    "rose": "#A69CAC",    # side panels
    "violet": "#474973",  # buttons / highlight
    "oxford": "#161B33",  # titles / headers
    "black": "#0D0C1D"    # dark footer / accents
}

HEADING_FONT = ("Cambria", 20, "bold")
SUBHEADING_FONT = ("Cambria", 14, "bold")
BODY_FONT = ("Georgia", 12)
BODY_FONT_BOLD = ("Georgia", 12, "bold")

class IEEE754GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IEEE-754 Calculator (32/64-bit) ✨")
        self.configure(bg=COLORS["almond"])
        self.geometry("1000x600")
        title = tk.Label(self, text="IEEE-754 Calculator (32/64-bit) 🧮",
                         font=HEADING_FONT, fg="white", bg=COLORS["oxford"])
        title.pack(fill="x", pady=5)
        container = tk.Frame(self, bg=COLORS["almond"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        self.left_frame = tk.Frame(container, bg=COLORS["rose"], bd=2, relief="ridge")
        self.left_frame.pack(side="left", fill="y", padx=5)
        self.right_frame = tk.Frame(container, bg=COLORS["rose"], bd=2, relief="ridge")
        self.right_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.precision = tk.StringVar(value="32")
        tk.Label(self.left_frame, text="Precision:", font=SUBHEADING_FONT, bg=COLORS["rose"]).pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(self.left_frame, text="32-bit", variable=self.precision, value="32", bg=COLORS["rose"]).pack(anchor="w", padx=5)
        tk.Radiobutton(self.left_frame, text="64-bit", variable=self.precision, value="64", bg=COLORS["rose"]).pack(anchor="w", padx=5)
        self.build_left_panel()
        self.build_right_panel()

    def build_left_panel(self):
        tk.Label(self.left_frame, text="🧮 Decimal Input:", font=SUBHEADING_FONT,
                 bg=COLORS["rose"], fg=COLORS["black"]).pack(anchor="w", padx=5, pady=5)
        self.decimal_entry = tk.Entry(self.left_frame, width=30, font=BODY_FONT)
        self.decimal_entry.pack(padx=5, pady=5)
        convert_btn = tk.Button(self.left_frame, text="➡ Convert Decimal → IEEE 754",
                                command=self.convert_decimal, bg=COLORS["violet"], fg="white", font=BODY_FONT_BOLD)
        convert_btn.pack(fill="x", padx=5, pady=5)
        tk.Label(self.left_frame, text="💻 IEEE 754 Input:",
                 font=SUBHEADING_FONT, bg=COLORS["rose"], fg=COLORS["black"]).pack(anchor="w", padx=5, pady=5)
        self.ieee_entry = tk.Entry(self.left_frame, width=65, font=BODY_FONT)
        self.ieee_entry.pack(padx=5, pady=5)
        convert_back_btn = tk.Button(self.left_frame, text="➡ Convert IEEE → Decimal",
                                     command=self.convert_ieee, bg=COLORS["violet"], fg="white", font=BODY_FONT_BOLD)
        convert_back_btn.pack(fill="x", padx=5, pady=5)
        tk.Label(self.left_frame, text="⚙ Operations",
                 font=SUBHEADING_FONT, bg=COLORS["rose"], fg=COLORS["black"]).pack(anchor="w", padx=5, pady=5)
        self.op_entry1 = tk.Entry(self.left_frame, width=15, font=BODY_FONT)
        self.op_entry2 = tk.Entry(self.left_frame, width=15, font=BODY_FONT)
        self.op_entry1.pack(padx=5, pady=2)
        self.op_entry2.pack(padx=5, pady=2)
        add_btn = tk.Button(self.left_frame, text="➕ Add",
                            command=self.add_op, bg=COLORS["violet"], fg="white", font=BODY_FONT_BOLD)
        add_btn.pack(fill="x", padx=5, pady=5)
        mul_btn = tk.Button(self.left_frame, text="✖ Multiply",
                            command=self.multiply_op, bg=COLORS["violet"], fg="white", font=BODY_FONT_BOLD)
        mul_btn.pack(fill="x", padx=5, pady=5)
        clear_btn = tk.Button(self.left_frame, text="🗑 Clear All",
                              command=self.clear_all, bg=COLORS["black"], fg="white", font=BODY_FONT_BOLD)
        clear_btn.pack(fill="x", padx=5, pady=5)

    def build_right_panel(self):
        tk.Label(self.right_frame, text="📊 Results", font=SUBHEADING_FONT,
                 bg=COLORS["rose"], fg=COLORS["black"]).pack(anchor="w", padx=5, pady=5)
        self.result_box = tk.Text(self.right_frame, height=5, bg="white", fg="black",
                                 wrap="word", font=BODY_FONT)
        self.result_box.pack(fill="x", padx=5, pady=5)
        tk.Label(self.right_frame, text="🔎 Output Breakdown", font=SUBHEADING_FONT,
                 bg=COLORS["rose"], fg=COLORS["black"]).pack(anchor="w", padx=5, pady=5)
        self.breakdown_box = tk.Text(self.right_frame, height=3, bg="white", fg="black",
                                   wrap="word", font=BODY_FONT)
        self.breakdown_box.pack(fill="x", padx=5, pady=5)
        self.learning_btn = tk.Button(self.right_frame,
                                      text="📘 Learning Mode — Step by Step", command=self.show_learning_mode,
                                      bg=COLORS["violet"], fg="white", font=BODY_FONT_BOLD)
        self.learning_btn.pack(fill="x", padx=5, pady=5)
        self.learning_text = tk.Text(self.right_frame, height=12, bg="white", fg="black",
                                   wrap="word", font=BODY_FONT)
        self.learning_text.pack(fill="both", padx=5, pady=5, expand=True)

    def convert_decimal(self):
        try:
            num = float(self.decimal_entry.get())
            if self.precision.get() == "32":
                binary = convert.float_to_ieee754(num)
            else:
                binary = convert.float_to_ieee754_64(num)
            self.ieee_entry.delete(0, tk.END)
            self.ieee_entry.insert(0, binary)
            self.result_box.insert(tk.END, f"Decimal {num} → IEEE754: {binary}\n")
            self.breakdown(binary)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convert_ieee(self):
        try:
            binary = self.ieee_entry.get()
            if self.precision.get() == "32":
                num = convert.ieee754_to_float(binary)
            else:
                num = convert.ieee754_to_float_64(binary)
            self.decimal_entry.delete(0, tk.END)
            self.decimal_entry.insert(0, str(num))
            self.result_box.insert(tk.END, f"IEEE754 {binary} → Decimal: {num}\n")
            self.breakdown(binary)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def breakdown(self, binary):
        if self.precision.get() == "32":
            s, e, m = binary[0], binary[1:9], binary[9:]
        else:
            s, e, m = binary[0], binary[1:12], binary[12:]
        self.breakdown_box.delete("1.0", tk.END)
        self.breakdown_box.insert(tk.END, f"S: {s}\nE: {e}\nM: {m}")

    def add_op(self):
        try:
            a, b = float(self.op_entry1.get()), float(self.op_entry2.get())
            if self.precision.get() == "32":
                res = ops.add_floats(a, b)
            else:
                res = ops.add_floats_64(a, b)
            self.result_box.insert(tk.END, f"Add: {a} + {b} = {res}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def multiply_op(self):
        try:
            a, b = float(self.op_entry1.get()), float(self.op_entry2.get())
            if self.precision.get() == "32":
                res = ops.multiply_floats(a, b)
            else:
                res = ops.multiply_floats_64(a, b)
            self.result_box.insert(tk.END, f"Multiply: {a} × {b} = {res}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_all(self):
        self.decimal_entry.delete(0, tk.END)
        self.ieee_entry.delete(0, tk.END)
        self.op_entry1.delete(0, tk.END)
        self.op_entry2.delete(0, tk.END)
        self.result_box.delete("1.0", tk.END)
        self.breakdown_box.delete("1.0", tk.END)
        self.learning_text.delete("1.0", tk.END)

    def show_learning_mode(self):
        binary = self.ieee_entry.get()
        if not binary:
            messagebox.showinfo("Info", "Please enter or convert a number first!")
            return
        if self.precision.get() == "32":
            s, e, m = binary[0], binary[1:9], binary[9:]
        else:
            s, e, m = binary[0], binary[1:12], binary[12:]
        self.learning_text.delete("1.0", tk.END)
        self.learning_text.insert(tk.END, "Step-by-Step Conversion:\n")
        self.learning_text.insert(tk.END, f"1. Sign bit: {s} → {'Positive' if s=='0' else 'Negative'}\n")
        self.learning_text.insert(tk.END, f"2. Exponent bits: {e} (biased)\n")
        self.learning_text.insert(tk.END, f"3. Mantissa bits: {m}\n")
        self.learning_text.insert(tk.END, "4. Reconstruct float using formula:\n")
        self.learning_text.insert(tk.END, " (-1)^S × (1.M) × 2^(E-bias)\n")

if __name__ == "__main__":
    app = IEEE754GUI()
    app.mainloop()
