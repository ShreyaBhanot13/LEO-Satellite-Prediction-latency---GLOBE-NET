# Streamlit Demo Manual

## Purpose Of This App

This app is a presentation-friendly network quality platform, branded as GLOBE-NET, built around an India-first story.

The main goal during the panel demo is to show that the platform can:

1. give a simple India-wide view
2. drill down into state-level patterns
3. show a focused Karnataka case
4. let the user test an example area interactively
5. provide supporting global context
6. explain the main drivers behind the results if the panel asks

The demo should sound like a practical service platform, not like a raw machine learning dashboard.

---

## Before The Demo

### What To Open

Keep these ready before the panel starts:

1. the Streamlit app in the browser
2. this manual
3. your slides, if you are also using slides

### How To Start The App

Open PowerShell in the project folder and run:

```powershell
C:/Users/250019004/AppData/Local/Programs/Python/Python314/python.exe -m streamlit run app.py --server.headless true --server.port 8501
```

Then open:

```text
http://localhost:8501
```

### Pre-Demo Checklist

Do these 5 to 10 minutes before the panel:

1. start the app
2. open it in the browser
3. do a hard refresh with `Ctrl+F5`
4. confirm the hero section, tabs, and charts load fully
5. click once through `Big Picture`, `Karnataka Focus`, and `Check Your Area`
6. keep the browser zoom at around `90%` or `100%`

---

## Recommended Demo Flow

Use this order for the panel:

1. Hero section
2. Big Picture
3. India Story
4. Karnataka Focus
5. Check Your Area
6. Global Snapshot
7. Network Drivers only if they ask how the system decides

If time is short, use this shorter order:

1. Hero section
2. Big Picture
3. Karnataka Focus
4. Check Your Area

---

## Step-By-Step Demo Script

## 1. Hero Section

### What To Do

Open the app and stay on the first screen for a few seconds.

### What To Say

"Good morning. This platform is designed to help review where internet quality looks stable and where some areas may need faster attention. The idea is to give a simple India-wide to area-level view in a way that is easy to understand visually."

"The app starts with a national view, then moves into state-level exploration, a Karnataka case study, an example area check, and finally supporting global and explainability views when needed."

### What The Panel Should Understand

The app is not just a static chart collection. It is a guided product-style interface.

---

## 2. Big Picture

### What To Click

Click the `Big Picture` tab.

### What To Show

1. the top summary metrics
2. the state ranking chart
3. the India map
4. the state table below

### What To Say

"This section gives the national overview. It helps us quickly identify which states appear more stable and which ones show stronger signs that some local areas may need attention."

"The left chart ranks states, and the map on the right makes the same story easier to see geographically. So instead of reading a large table first, the user gets an immediate visual summary."

"There is also a minimum-sample filter so the comparison remains fair and does not overemphasize very small cases."

### Safe Short Version

"This is the India-wide summary view. It helps users quickly see where attention appears more concentrated across states."

---

## 3. India Story

### What To Click

Click the `India Story` tab.

### What To Show

1. select a state, usually keep `Karnataka`
2. show the India map emphasis dropdown
3. show the selected state's zone map
4. show the operator context charts if visible

### What To Say

"This section moves from national view to state-level exploration. I can choose a state and also decide what the India map should emphasize, for example attention level, reported weaker areas, or slower-response conditions."

"On the left, we keep the national context. On the right, we zoom into the selected state's zones. This helps the user move naturally from big-picture understanding into more local detail."

"Below that, the app adds simple telecom context for the selected state, such as operator presence and average speed differences, so the view is broader than just one score."

### Good Demo Practice

Do not keep changing many states. Change at most once if you want to show that the app is interactive.

---

## 4. Karnataka Focus

### What To Click

Click the `Karnataka Focus` tab.

### What To Show

1. the Karnataka metrics at the top
2. the Karnataka zone map
3. the short summary on the right
4. the table of Karnataka areas most likely to need attention

### What To Say

"We use Karnataka as a focused case study so that the panel can see a complete state-level example in more detail."

"At the top, the app shows the number of reviewed areas, the number flagged, the flag rate, and the observed weaker-area rate."

"The map helps identify where stronger attention patterns appear inside the state, while the table below gives the more specific local areas that stand out."

"This makes the platform more actionable because we are not stopping at only the state name; we are able to narrow down to local patterns."

### Safe Short Version

"Karnataka is our detailed example state. This section shows how the platform narrows from state view to local area view."

---

## 5. Check Your Area

This is the most interactive part of the demo and usually the strongest section to show the panel.

## What This Section Does

The `Check Your Area` tab lets you simulate an example area and see whether it looks comparatively stable or more likely to need attention.

It works by combining:

1. the selected state
2. an example area from that state
3. a starting scenario
4. simple user-facing condition sliders

This makes it useful as a decision-support view rather than only a reporting view.

## What To Click

Click the `Check Your Area` tab.

Keep these steps simple:

1. choose `Karnataka`
2. pick a scenario
3. choose the example area carefully
4. adjust the simple controls
5. click `Score this zone`

Important practical note:

In Karnataka, `Better-performing example area` usually remains stable even under stressed settings. If you want a stronger live demo result, use `Higher-risk example area`.

## How To Explain The Inputs

### Choose A State

This sets the state-level comparison baseline.

What to say:

"The app compares an area against typical conditions in the chosen state, so the state selection matters because a stressed area in one state may look different from a stressed area in another."

### Starting Situation

These scenario choices change the starting template before your manual adjustments.

Use this explanation:

1. `Keep it similar` means start close to the example area's existing pattern
2. `Rush-hour stress` means conditions are pushed toward congestion and weaker stability
3. `Network upgrade` means conditions are pushed in a better direction
4. `Sudden demand spike` means unusual pressure appears quickly

What to say:

"This lets us demonstrate how the same area may behave differently under different operating conditions."

### Example Area

This picks a real sample-like template from the selected state.

What to say:

"Instead of entering raw technical values manually, the app starts from an example area and then lets us adjust it with simple controls. That keeps the interface easier to use."

Extra practical note:

"If I want to demonstrate a more clearly stressed result, I should use the higher-risk example area. If I use the better-performing example area, it may still stay stable even after stress is added."

### The Four Simple Controls

These are the easiest way to explain the section:

1. `Connection strength`: how strong the connection feels
2. `Traffic load`: how busy the network is
3. `Crowding`: how many users or devices seem to be sharing the area
4. `Connection stability`: how steady or unstable the connection is

What to say:

"These controls were intentionally designed in plain language so a reviewer can interact with the app without needing to know the backend technical variables."

## How To Explain The Output

After clicking `Score this zone`, the app shows:

1. a gauge
2. a simple outcome label
3. a short interpretation
4. the change from the starting example
5. a comparison chart against a typical area in the same state

What to say:

"The output does not just give a number. It gives a readable assessment, shows how different this area is from the starting example, and then compares the area with a typical area in the same state."

"That makes the result easier to explain in practical terms."

---

## Check Your Area Demo Examples

Use one or two examples only. Do not do too many.

## Example 1: Busy Area Under Stress

### What To Set

1. State: `Karnataka`
2. Starting situation: `Rush-hour stress`
3. Example area: `Higher-risk example area`
4. Connection strength: `Weak`
5. Traffic load: `Very busy`
6. Crowding: `Very crowded`
7. Connection stability: `Very unstable`

Expected result:

This should move into `Needs attention likely`. In testing, this Karnataka setup produced an attention score around `58.9%`.

### What To Say Before Clicking Score

"Here I am simulating a busier and more stressed situation. The connection is weaker, traffic is high, the area is crowded, and stability is lower."

### What To Say After The Result Appears

"In this case, the app should move the area toward needing more attention because the conditions are now closer to a congested or stressed operating situation."

"The comparison chart below helps explain why, because it shows how this area differs from a more typical area in the same state."

## Example 2: Same Area After Improvement

### What To Set

1. State: `Karnataka`
2. Starting situation: `Network upgrade`
3. Example area: `Higher-risk example area`
4. Connection strength: `Good` or `Very good`
5. Traffic load: `Typical` or `Light`
6. Crowding: `Typical` or `Sparse`
7. Connection stability: `Stable` or `Very stable`

Expected result:

This should move the same area back toward a more stable outcome. In testing, the Karnataka `Higher-risk example area` with `Network upgrade` dropped to about `30.5%`.

### What To Say Before Clicking Score

"Now I am taking a similar area but applying more favorable conditions, as if capacity has improved and the connection is more stable."

### What To Say After The Result Appears

"Here the area should move in a more stable direction compared with the previous stressed example. This helps show that the section is not only descriptive; it can also be used to test simple what-if conditions."

## Example 3: Sudden Demand Shock

### What To Set

1. State: `Karnataka` or another state if you want to show variety
2. Starting situation: `Sudden demand spike`
3. Example area: `Higher-risk example area`
4. Connection strength: `Weak` or `Very weak`
5. Traffic load: `Very busy`
6. Crowding: `Very crowded`
7. Connection stability: `Typical` or `Unstable`

Expected result:

This can also cross into a higher-attention result. In testing with Karnataka, this type of setup moved above `50%`.

### What To Say

"This example represents a sudden pressure increase, such as an event, temporary congestion, or a spike in usage. The point here is to show how quickly the area view can be rechecked under changing conditions."

---

## 6. Global Snapshot

### What To Click

Click the `Global Snapshot` tab.

### What To Show

1. the world map
2. the spotlight cards
3. the foreign reference charts

### What To Say

"This section is supporting context only. India remains the primary coverage story. Here, we briefly show where the service sits globally and include earlier reference context from Germany and the Netherlands."

"The purpose is simply to show that the broader approach was also reviewed against international reference data."

### Important Note

Do not stay too long here. Keep this short unless they ask specifically.

---

## 7. Network Drivers

### When To Use This

Only go here if the panel asks:

1. how the system decides
2. what factors matter most
3. whether the outputs are explainable

### What To Say

"This section explains the main signals behind the results. It shows which feature groups and which individual signals are most closely linked to areas that may need attention."

"I usually keep this as a supporting transparency view, because the main user journey is meant to stay simple."

### Important Note

Do not start your demo here.

---

## Full Panel Speaker Notes

You can read this almost directly.

"Good morning. This platform is designed to present internet quality insights in a simple, user-friendly way. It helps show where service looks stable, where it appears stretched, and which states or local areas may need faster attention."

"The app follows a top-down structure. It begins with an India-wide view, then moves into state-level exploration, then a Karnataka case study, and then an interactive area-level check. After that, it includes a short global reference section and an explainability section if needed."

"In the Big Picture view, we can quickly understand the national pattern. Instead of starting with raw technical tables, the app provides a ranking view and a geographic map so the user can identify stronger attention areas more naturally."

"In the India Story view, we move into a selected state. This helps connect the national picture with local geographic patterns and also adds operator context for a more complete service view."

"In the Karnataka Focus section, we use one state as a concrete case study. This helps show how the platform narrows from state-level insight to more specific local areas that stand out."

"The Check Your Area section is the most interactive part. It allows the user to start from an example area, apply simple real-world conditions like stronger traffic or weaker stability, and then check whether the area looks comparatively stable or more likely to need attention."

"The Global Snapshot section is included only as supporting international context. The app remains India-first."

"If needed, the Network Drivers section explains the main signals influencing the results, which helps with transparency and interpretability."

"Overall, the strength of this platform is that it turns a large amount of network-quality analysis into an interface that is easier to explore, explain, and use during review."

---

## What Not To Say

Avoid saying:

1. "This is just a demo dashboard"
2. "This is mainly an ML model viewer"
3. "This tab is only technical"
4. "These are only backend metrics"
5. "I will now show the model internals" unless they specifically ask

Prefer saying:

1. "This platform helps review where network quality may need attention"
2. "This gives an India-wide to area-level view"
3. "This is supporting context"
4. "This helps explain the result in a readable way"

---

## If The Panel Asks Questions

### If They Ask Why Karnataka

"Karnataka is used as a focused case study so the panel can see one state in detail rather than staying only at national level."

### If They Ask What The Score Means

"It is a simple attention indicator showing whether the area looks comparatively stable or more likely to need attention relative to similar state conditions."

### If They Ask Whether This Is Real-Time

"For this presentation, the app is reading prepared processed outputs so that the user experience stays fast and stable during review."

### If They Ask Why Foreign Data Is Included

"That section is only supporting international reference context. The main story and main service view remain India-first."

### If They Ask How To Read The Check Area Result

"The result combines a simple gauge, a readable summary, and a comparison against a typical area in the same state, so the user gets both a quick answer and a reasoned comparison."

---

## Troubleshooting During Demo

### If A Chart Looks Wrong

Refresh the browser once.

### If The App Seems Slow

Wait a few seconds after switching tabs because some charts are heavier than others.

### If You Lose Track During Speaking

Come back to this sentence:

"The main point of this platform is to move from India-wide understanding to state-level detail and then to a practical area-level check."

---

## Final Closing Line

"To summarize, this app provides a simple way to move from national network-quality patterns to state and local review, while also supporting scenario testing and explainable results in one interface."