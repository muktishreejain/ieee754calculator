# IEEE 754 Floating-Point Calculator (Python GUI)

A Python app to convert **decimal ↔ IEEE 754** (single/double precision), visualize **sign / exponent / mantissa**, and (later) perform **add/multiply** with an educational **Learning Mode**.

## ✨ Features
- Decimal → IEEE-754 bits and IEEE-754 bits → Decimal
- Single (32-bit) and Double (64-bit)
- Color-coded output: Sign (red), Exponent (blue), Mantissa (green)
- Learning Mode (planned): step-by-step normalization, bias, mantissa build

## 🧩 Architecture & Roles
- **Person A (Backend):** Bit-level IEEE-754 conversions, ops, tests
- **Person B (GUI):** Tkinter/PyQt UI, validation, wiring to backend
- **Person C (Viz & Docs):** Step-through explanations, README, slides

ieee754-gui/
├─ app.py # GUI (Person B)
├─ backend_ieee.py # Backend contract (Person A implements)
├─ mock_backend_ieee.py # Temporary mock so GUI runs now
└─ tests/ # (Person A) Unit tests

