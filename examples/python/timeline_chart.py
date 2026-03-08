"""
ACS WhatsApp Integration Timeline Chart
Creates a visualization of the ACS WhatsApp integration milestones
and Alexandre Pedrosa's anticipation timeline.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8')

# Define events and dates
events = [
    "ACS Advanced Messaging launched\n(basic WhatsApp integration)",
    "Alexandre Pedrosa documents\nAI Mesh & Interoperability",
    "Meta introduces new pricing model\n(Commercial change only)",
    "ACS expands with Azure AI + Dynamics 365\n(Native AI in WhatsApp)"
]

dates = [
    datetime(2024, 3, 1),
    datetime(2025, 12, 1),
    datetime(2026, 1, 1),
    datetime(2026, 2, 15)  # Approximate "early 2026"
]

# Create plot
fig, ax = plt.subplots(figsize=(10, 4))

# Plot vertical lines and annotate
for i, (event, date) in enumerate(zip(events, dates)):
    ax.axvline(date, color='tab:blue', linestyle='--', ymax=0.8)
    ax.text(date, 1.02, event, rotation=45, ha='right', va='bottom', fontsize=9)

# Format x-axis
ax.set_xlim(datetime(2024, 1, 1), datetime(2026, 6, 1))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

# Remove y-axis and add title
ax.get_yaxis().set_visible(False)
ax.set_title("Timeline: ACS WhatsApp Integration vs Alexandre Pedrosa's Anticipation", 
             fontsize=12, weight='bold')

# Adjust layout and save
plt.tight_layout()
output_path = "acs_whatsapp_timeline.png"
plt.savefig(output_path)

print(f"Timeline chart created showing ACS WhatsApp integration milestones.")
print(f"Saved as {output_path}")
