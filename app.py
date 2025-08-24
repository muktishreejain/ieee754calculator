# app.py
"""
Tkinter GUI for IEEE-754 converter and simple ops.
Uses:
 - convert.float_to_ieee754
 - convert.ieee754_to_float
 - ops.add_ieee754
 - ops.multiply_ieee754

Assumes 32-bit IEEE-754 functions in convert.py (as provided).
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import convert
import ops
import utils


# Try local package-style imports (if project is packaged)
try:
    from convert import float_to_ieee754, ieee754_to_float
    from ops import add_ieee754, multiply_ieee754
    from utils import shift_left, shift_right
except Exception as e:
    # fallback - user likely running from the same dir; try non-package import
    try:
        import convert
        from convert import float_to_ieee754, ieee754_to_float
        import ops
        from ops import add_ieee754, multiply_ieee754
        import utils
        from utils import shift_left, shift_right
    except Exception as ee:
        message = (
            "Failed to import project modules. Make sure convert.py, ops.py and utils.py "
            "are present in the same folder as app.py."
        )
        raise ImportError(message) from ee

APP_TITLE = "IEEE-754 Calculator (32-bit) — GUI"
WINDOW_SIZE = "900x650"

# ---------- Helpers ----------
def format_bits(bits: str, group: int = 4) -> str:
    """Return bits spaced by group for readability."""
    bits = bits.replace(" ", "")
    return " ".join(bits[i:i+group] for i in range(0, len(bits), group))

def split_bits(bits: str):
    """Return (sign, exponent, mantissa) for 32-bit representation."""
    bits = bits.replace(" ", "")
    if len(bits) != 32:
        raise ValueError("Expected 32 bits for single precision.")
    sign = bits[0]
    exp = bits[1:9]
    man = bits[9:]
    return sign, exp, man

def exponent_value(exp_bits: str) -> int:
    """Return integer exponent minus bias for single precision."""
    bias = 127
    e_int = int(exp_bits, 2)
    return e_int - bias

def mantissa_value(man_bits: str, exp_bits: str):
    """Return normalized mantissa float (including implicit leading 1 if normal)."""
    is_denorm = (int(exp_bits, 2) == 0)
    if is_denorm:
        # no implicit leading 1
        mant = 0.0
        for i, b in enumerate(man_bits, start=1):
            mant += int(b) * (2 ** -i)
        return mant
    else:
        mant = 1.0  # implicit leading 1
        for i, b in enumerate(man_bits, start=1):
            mant += int(b) * (2 ** -i)
        return mant

def detect_special(exp_bits: str, man_bits: str):
    e_int = int(exp_bits, 2)
    m_int = int(man_bits, 2)
    if e_int == 0 and m_int == 0:
        return "Zero"
    if e_int == 0 and m_int != 0:
        return "Denormal (subnormal)"
    if e_int == 255 and m_int == 0:
        return "Infinity"
    if e_int == 255 and m_int != 0:
        return "NaN"
    return "Normal"

# ---------- GUI ----------
class IEEEApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(True, True)

        # State vars
        self.dec_in_var = tk.StringVar()
        self.bin_in_var = tk.StringVar()
        self.dec_out_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.learning_mode = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        padx = 12
        pady = 8

        header = tk.Label(self, text=APP_TITLE, font=("Segoe UI", 16, "bold"))
        header.pack(pady=(10, 6))

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Left column: inputs / controls
        left = ttk.Frame(main_frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)

        # Right column: outputs / learning panel
        right = ttk.Frame(main_frame)
        right.grid(row=0, column=1, sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # -- Inputs
        input_frame = ttk.LabelFrame(left, text="Inputs", padding=10)
        input_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(input_frame, text="Decimal:").grid(row=0, column=0, sticky="e")
        dec_entry = ttk.Entry(input_frame, textvariable=self.dec_in_var, width=28)
        dec_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Button(input_frame, text="Decimal → IEEE", command=self.on_decimal_to_ieee)\
            .grid(row=0, column=2, sticky="w", padx=6)

        ttk.Label(input_frame, text="IEEE 754 (32-bit):").grid(row=1, column=0, sticky="e")
        bin_entry = ttk.Entry(input_frame, textvariable=self.bin_in_var, width=40)
        bin_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=6, pady=4)

        ttk.Button(input_frame, text="IEEE → Decimal", command=self.on_ieee_to_decimal)\
            .grid(row=1, column=3, sticky="w", padx=6)

        # Ops frame
        ops_frame = ttk.LabelFrame(left, text="Operations", padding=10)
        ops_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(ops_frame, text="Operand A (decimal):").grid(row=0, column=0, sticky="e")
        self.op_a = ttk.Entry(ops_frame, width=18)
        self.op_a.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(ops_frame, text="Operand B (decimal):").grid(row=1, column=0, sticky="e")
        self.op_b = ttk.Entry(ops_frame, width=18)
        self.op_b.grid(row=1, column=1, padx=6, pady=4)

        ttk.Button(ops_frame, text="Add (use ops.add_ieee754)", command=self.on_add).grid(row=2, column=0, padx=6, pady=8)
        ttk.Button(ops_frame, text="Multiply (use ops.multiply_ieee754)", command=self.on_multiply)\
            .grid(row=2, column=1, padx=6, pady=8)

        # Clear and precision note
        ttk.Button(left, text="Clear All", command=self.on_clear).pack(fill="x", pady=(0, 8))
        ttk.Label(left, text="Note: Using 32-bit single precision (current backend).", foreground="gray").pack(anchor="w")

        # Learning mode toggle
        lm_frame = ttk.Frame(left)
        lm_frame.pack(fill="x", pady=(4, 12))
        ttk.Checkbutton(lm_frame, text="Learning Mode (show breakdown)", variable=self.learning_mode,
                        command=self._render_learning_panel).pack(anchor="w")

        # -- Outputs (right)
        out_frame = ttk.LabelFrame(right, text="Result", padding=10)
        out_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(out_frame, text="Decimal Output:").grid(row=0, column=0, sticky="e")
        self.dec_out_entry = ttk.Entry(out_frame, textvariable=self.dec_out_var, width=28, state="readonly")
        self.dec_out_entry.grid(row=0, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(out_frame, text="IEEE 754 (S | E | M):").grid(row=1, column=0, sticky="ne")
        bits_frame = ttk.Frame(out_frame)
        bits_frame.grid(row=1, column=1, sticky="w")

        self.lbl_sign = tk.Label(bits_frame, text="", font=("Consolas", 12, "bold"), fg="red")
        self.lbl_exp  = tk.Label(bits_frame, text="", font=("Consolas", 12, "bold"), fg="blue")
        self.lbl_man  = tk.Label(bits_frame, text="", font=("Consolas", 12, "bold"), fg="green")
        self.lbl_sign.grid(row=0, column=0, sticky="w")
        self.lbl_exp.grid(row=0, column=1, sticky="w")
        self.lbl_man.grid(row=0, column=2, sticky="w")

        # Full-bit formatted display
        ttk.Label(out_frame, text="Full bits (grouped):", foreground="gray").grid(row=2, column=0, sticky="e")
        self.full_bits_label = ttk.Label(out_frame, text="", font=("Consolas", 11))
        self.full_bits_label.grid(row=2, column=1, sticky="w")

        # Learning/Breakdown panel (scrollable)
        learn_frame = ttk.LabelFrame(right, text="Learning Mode — Breakdown", padding=8)
        learn_frame.pack(fill="both", expand=True)

        self.learn_text = scrolledtext.ScrolledText(learn_frame, height=12, wrap="word", state="disabled")
        self.learn_text.pack(fill="both", expand=True)

        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", padx=10, pady=(6, 12))
        ttk.Label(status_bar, textvariable=self.status_var, foreground="gray").pack(side="left")

    # ---------- Actions ----------
    def on_decimal_to_ieee(self):
        self.status_var.set("")
        raw = self.dec_in_var.get().strip()
        if raw == "":
            messagebox.showinfo("Input required", "Enter a decimal value to convert.")
            return
        try:
            # Accept special floats too via Python float()
            val = float(raw)
            bits = float_to_ieee754(val)
            self._set_result_from_bits(bits)
            self.status_var.set(f"Converted decimal {val} → bits")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Could not convert decimal: {e}")
            self.status_var.set(f"Error: {e}")

    def on_ieee_to_decimal(self):
        self.status_var.set("")
        bits = self.bin_in_var.get().replace(" ", "")
        try:
            if not all(ch in "01" for ch in bits):
                raise ValueError("Bits must contain only 0 and 1.")
            if len(bits) != 32:
                raise ValueError("IEEE 754 single precision requires exactly 32 bits.")
            val = ieee754_to_float(bits)
            self.dec_out_var.set(str(val))
            self._set_result_from_bits(bits)
            self.status_var.set("Converted bits → decimal")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Could not convert IEEE bits: {e}")
            self.status_var.set(f"Error: {e}")

    def on_add(self):
        self.status_var.set("")
        a = self.op_a.get().strip()
        b = self.op_b.get().strip()
        try:
            if a == "" or b == "":
                raise ValueError("Enter both operands for Add.")
            a_f = float(a)
            b_f = float(b)
            # Convert to bits then use ops.add_ieee754
            a_bits = float_to_ieee754(a_f)
            b_bits = float_to_ieee754(b_f)
            sum_bits = add_ieee754(a_bits, b_bits)
            sum_val = ieee754_to_float(sum_bits)
            self.dec_out_var.set(str(sum_val))
            self._set_result_from_bits(sum_bits)
            self.status_var.set(f"Added {a} + {b} (via ops.add_ieee754)")
        except Exception as e:
            messagebox.showerror("Add Error", str(e))
            self.status_var.set(f"Error: {e}")

    def on_multiply(self):
        self.status_var.set("")
        a = self.op_a.get().strip()
        b = self.op_b.get().strip()
        try:
            if a == "" or b == "":
                raise ValueError("Enter both operands for Multiply.")
            a_f = float(a)
            b_f = float(b)
            a_bits = float_to_ieee754(a_f)
            b_bits = float_to_ieee754(b_f)
            mul_bits = multiply_ieee754(a_bits, b_bits)
            mul_val = ieee754_to_float(mul_bits)
            self.dec_out_var.set(str(mul_val))
            self._set_result_from_bits(mul_bits)
            self.status_var.set(f"Multiplied {a} * {b} (via ops.multiply_ieee754)")
        except Exception as e:
            messagebox.showerror("Multiply Error", str(e))
            self.status_var.set(f"Error: {e}")

    def on_clear(self):
        self.dec_in_var.set("")
        self.bin_in_var.set("")
        self.dec_out_var.set("")
        self.op_a.delete(0, tk.END)
        self.op_b.delete(0, tk.END)
        self._clear_bits_display()
        self.learn_text.configure(state="normal")
        self.learn_text.delete("1.0", tk.END)
        self.learn_text.configure(state="disabled")
        self.status_var.set("Cleared.")

    # ---------- UI helpers ----------
    def _set_result_from_bits(self, bits: str):
        # show full grouped bits
        grouped = format_bits(bits, group=4)
        self.full_bits_label.config(text=grouped)
        # color split
        try:
            s, e, m = split_bits(bits)
            self.lbl_sign.configure(text=s + " ")
            self.lbl_exp.configure(text=e + " ")
            self.lbl_man.configure(text=m)
        except Exception:
            self._clear_bits_display()
        # also set binary input (so users can copy)
        self.bin_in_var.set(bits)
        # populate learning panel if on
        self._render_learning_panel()

    def _clear_bits_display(self):
        self.lbl_sign.configure(text="")
        self.lbl_exp.configure(text="")
        self.lbl_man.configure(text="")
        self.full_bits_label.config(text="")

    def _render_learning_panel(self):
        if not self.learning_mode.get():
            # clear
            self.learn_text.configure(state="normal")
            self.learn_text.delete("1.0", tk.END)
            self.learn_text.configure(state="disabled")
            return

        bits = self.bin_in_var.get().replace(" ", "")
        if not bits or len(bits) != 32 or any(ch not in "01" for ch in bits):
            # Nothing to explain
            self.learn_text.configure(state="normal")
            self.learn_text.delete("1.0", tk.END)
            self.learn_text.insert(tk.END, "Learning Mode: enter a valid 32-bit representation or convert a decimal first.\n")
            self.learn_text.configure(state="disabled")
            return

        try:
            s, e, m = split_bits(bits)
            e_int = int(e, 2)
            m_int = int(m, 2)
            special = detect_special(e, m)

            bias = 127
            exponent_signed = e_int - bias
            mantissa_norm = mantissa_value(m, e)
            # Build explanation text
            txt_lines = []
            txt_lines.append(f"Full bits: {format_bits(bits, 4)}\n")
            txt_lines.append(f"Sign bit: {s} → {'Negative' if s == '1' else 'Positive'}\n")
            txt_lines.append(f"Exponent bits: {e} (binary) → {e_int} (unsigned)\n")
            txt_lines.append(f"Bias for single precision: {bias}\n")
            txt_lines.append(f"Exponent (signed) = {e_int} - {bias} = {exponent_signed}\n")
            txt_lines.append(f"Mantissa bits: {m} (binary) → {m_int} (unsigned)\n")
            txt_lines.append(f"Detected classification: {special}\n")

            if special == "Normal":
                txt_lines.append(f"Normalized mantissa (1.fraction): {mantissa_norm}\n")
            elif special == "Denormal (subnormal)":
                txt_lines.append("Denormal number: exponent is 0, no implicit leading 1.\n")
                txt_lines.append(f"Fractional mantissa value: {mantissa_norm}\n")
            elif special == "Zero":
                txt_lines.append("This represents +0 or -0 depending on sign bit.\n")
            elif special == "Infinity":
                txt_lines.append("This represents +∞ or -∞ depending on sign bit.\n")
            elif special == "NaN":
                txt_lines.append("Not a Number (NaN). Mantissa non-zero with exponent all 1s.\n")

            # Show the reconstructed float using backend
            try:
                reconstructed = ieee754_to_float(bits)
                txt_lines.append(f"\nReconstructed float (using convert.ieee754_to_float): {reconstructed}\n")
            except Exception as e:
                txt_lines.append(f"\nReconstructed float: error ({e})\n")

            # Combine & show
            content = "\n".join(txt_lines)
            self.learn_text.configure(state="normal")
            self.learn_text.delete("1.0", tk.END)
            self.learn_text.insert(tk.END, content)
            self.learn_text.configure(state="disabled")
        except Exception as e:
            self.learn_text.configure(state="normal")
            self.learn_text.delete("1.0", tk.END)
            self.learn_text.insert(tk.END, f"Could not render learning panel: {e}")
            self.learn_text.configure(state="disabled")

# ---------- Run ----------
if __name__ == "__main__":
    app = IEEEApp()
    app.mainloop()
