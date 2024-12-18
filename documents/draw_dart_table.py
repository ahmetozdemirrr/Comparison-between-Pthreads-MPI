import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(6, 6))

# draw square
square = plt.Rectangle((-1, -1), 2, 2, fill=None, edgecolor='blue', linewidth=2, label="Square (2x2)")
ax.add_patch(square)

# draw circle
circle = plt.Circle((0, 0), 1, fill=None, edgecolor='red', linewidth=2, label="Circle (radius=1)")
ax.add_patch(circle)

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal', adjustable='box')

# title and decscriptions
plt.title("Dartboard with Square and Inscribed Circle", fontsize=14)
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
plt.legend()

plt.show()
