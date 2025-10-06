# 🧙 Goblin Laws

Ancient wisdoms of the Goblin folk, written down so that future builders, tinkerers, and bug-chasers may not forget.

Each law carries a number, not in order of discovery, but in the order of Goblin Time, sometimes backwards, sometimes sideways.

---

## 🗂️ Goblin Law Numbering Convention

- **#1–19: Foundational Goblinisms**
  Universal truths of tinkering, mischief, and survival. The sort of stuff carved into cave walls.
  _(Ex: “A Goblin never trusts a clean lever.”)_
- **#20–39: Programming & Systems**
  How goblins wire things up without blowing the mushroom farm.
  _(Ex: Law #37 – Never Meddle in Another Goblin’s Guts)_
- **#40–59: Music & Soundcraft**
  Rules for banging pots, tuning pipes, and stroking strings until they sing.
  _(Ex: “If the beat limps, the goblin stumbles.”)_
- **#60–79: Governance & Trade**
  How goblins argue, share loot, and keep the watchfires burning.
  _(Ex: “A goblin who hides their ledger hides their shame.”)_
- **#80–99: Forbidden & Foolish**
  Warnings, curses, and “things we did once and will never do again.”
  _(Ex: “Never lick the glowing mushrooms. Not even a nibble.”)_
- **#100: The Unwritten Law**
  Always blank, always waiting. The goblins say if it’s ever written down, the world ends.

---

# Foundational Goblinisms 1-19

## ⚖️ Goblin Law #5 – _Raise the Fist_

A goblin never bows to silence, nor bends to those who would chain the song.

When the hall is dark, the fist is raised,

for **solidarity**, for **movement**, for **defiance**.

It is not a hand for meddling (that’s Law #37’s warning),

but a hand for saying **“we build together, we resist together.”**

**Rule of Thumb:**

If a goblin’s work, be it rack, bus, or beat,

does not carry a spark of resistance,

then it is just tinkering, not Tonika.

## ⚖️ Goblin Law #6 – _The Rule of Rules_

Some laws live only in one burrow: about pipes, or pots, or trade.

But when a law echoes across many halls, from mushrooms to markets, from code to chords, it must be carved into the **Foundational Stones (1–19)**.

Thus the goblin lawbook stays lean and sly, not bloated with copies.

One carving, many echoes.

This keeps creativity uncrushed, while ensuring no goblin argues:

“Does this belong in Systems or Trade?”, the stone already answers.

**Rule of Thumb:**
If a law wears more than one hat, it belongs among the first nineteen.

## ⚖️ Goblin Law #7 – _No Fat Orcs_

A goblin, or a goblin’s work, must do **one thing well, and only that**.

Catch, calculate, display, export, persist, but never all at once.

A pot that tries to be a drum, a helmet, and a cooking pan ends up dented and burnt.

Each piece, like each goblin, stays **lean and fast**, carrying just enough to fulfill its promise.

The heavy lifting, cataloguing, publishing, storing, shipping, polishing, belongs to other goblins down the chain.

Every Fat Orc slows the Bus.

When a module, a project, or even a goblin life swells with too many concerns, the Committee declares it **Fat** and sends it off to the **Fitness Program (modularisation)** , splitting work into smaller, truer parts.

**Rule of Thumb:**
If you wouldn’t carve it on a single stone tablet or carry it on your back up a mountain, it’s trying to do too much.

## ⚖️ Goblin Law #8 – _All Goblins Are Boundary Guards_

No goblin is excused from the edges.

Every goblin meets the Outside, raw bytes, strangers at the gate, the shifting weather.

But the test of a goblin’s worth is not in the meeting,

but in how swiftly and cleanly they pass the news to the **Bus**.

Delay breeds drift.

Hoarding breeds shadow.

Side-channels breed chaos.

The Bus must always be the **first place the Outside is written down**.

**Rule of Thumb:**
Every goblin may touch the wild, but all goblins are **boundary guards**.
If you don’t hand it to the Bus, you’ve already failed your watch.

## ⚖️ Goblin Law #13 – _Keep the Guest List Clean_

A goblin hall is only as orderly as its guest list.

If every goblin scrawls their own marks, soon the page is torn, the ink smudged, and no one knows who’s truly in the room.

So one scribe keeps the book, and all goblins read from it.

Names spelled the same, marks in the same place, and smudges wiped away.

Thus clans share a **single, trusted record** , of who’s present, what’s owed, and what’s been played.

Not a dozen half-scribbled ledgers, but one **clean guest list** that all can trust.

**Rule of Thumb:**
If two goblins argue over “what’s in the book,” you need a cleaner list.

# Programming & Systems 20-39

## ⚖️ Goblin Law #32 – _Never Patch a Monkey_

When goblins strap new tails onto old monkeys,

the beast runs wild, stealing fruit and smashing pots.

So it is with code:

patching another’s functions, twisting their shape,

makes the whole hall brittle and afraid.

If a goblin must change a thing,

they raise a **new module** with its own name and song,

never disguising their mischief as another’s work.

**Rule of Thumb:**
Extend, don’t overwrite.
Compose, don’t contort.
A monkey patched is a monkey enraged.

## ⚖️ Goblin Law #37 – _Never Meddle in Another Goblin’s Guts_

When one goblin module pokes about inside another’s squishy bits, chaos follows.

Boundaries blur, secrets spill, and soon the whole den stinks of burnt mushrooms.

Wise goblins use the Bus: speak your need, let the message travel, and let the other goblin respond in their own way.

Thus modules stay sturdy, secrets stay secret, and no one wakes up to find their levers pulled without asking.

**Rule of Thumb:**
If goblins bypass the Bus and meddle directly, it always ends in burnt mushrooms.
If it rides the Bus, it’s future-proof.

**Tonika-Bus is the central event backbone for the whole Tonika ecosystem.** Its job is to handle all module communication in a single, consistent way, so no module needs its own emitter or custom wiring. Every component (keyboard, chord engine, stream module, etc.) should subscribe and publish only through the bus. When cleaning up legacy code, look for direct emitter calls, one-off event dispatchers, or modules mutating each other directly, those need to be replaced with `tonika-bus` events. The rule of thumb: _if it’s handling events outside the bus, it’s legacy; if it’s on the bus, it’s future-proof._

# Music & Soundcraft 40-59

## ⚖️ Goblin Law #41 – Only One Drumbeat of Readiness

From the pit there comes but one count-in.

The drummer’s quiet tap, the conductor’s nod —

that is enough to set the hall in motion.

Let not every goblin shout their own “ready,”

for a dozen false starts tear the tune to rags.

Thus in Tonika:

the **Base Class** alone beats the lifecycle drum —

_initializing, ready, error_.

Modules, once cued, may bellow their own riffs —

notes, chords, bends, loops —

but none may strike the drum of readiness again.

**Rule of Thumb:**
Silence before the song.
One clear beat to begin.
Then play on.

# Governance & Trade 60-79

# Forbidden & Foolish 80-99

# The Unwritten Law 100