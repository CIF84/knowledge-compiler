# SPEC-064 — Owner review

Owner verdict: PENDING. Promotion: NOT_AUTHORIZED.

Review R0 through R3 for each case, then inspect the measurement table and exact recovery ledger.

Mechanical finding: GROUPING_REMAINS_NON_ABSTRACTIVE
Architecture finding: BOUNDED_MODEL_CANDIDATE_REQUIRES_SEPARATE_AUTHORIZATION

Source integration and schema grouping are measured separately. Carrier counts are not cognitive scores.

## 1. Understanding plate motions

### R0

```text
Divergent boundaries occur along spreading centers where plates are moving apart and new crust is created by magma pushing up from the mantle. Picture two giant conveyor belts, facing each other but slowly moving in opposite directions as they transport newly formed oceanic crust away from the ridge crest.

Perhaps the best known of the divergent boundaries is the Mid-Atlantic Ridge. This submerged mountain range, which extends from the Arctic Ocean to beyond the southern tip of Africa, is but one segment of the global mid-ocean ridge system that encircles the Earth. The rate of spreading along the Mid-Atlantic Ridge averages about 2.5 centimeters per year (cm/yr), or 25 km in a million years. This rate may seem slow by human standards, but because this process has been going on for millions of years, it has resulted in plate movement of thousands of kilometers. Seafloor spreading over the past 100 to 200 million years has caused the Atlantic Ocean to grow from a tiny inlet of water between the continents of Europe, Africa, and the Americas into the vast ocean that exists today.

The volcanic country of Iceland, which straddles the Mid-Atlantic Ridge, offers scientists a natural laboratory for studying on land the processes also occurring along the submerged parts of a spreading ridge. Iceland is splitting along the spreading center between the North American and Eurasian Plates, as North America moves westward relative to Eurasia.

The consequences of plate movement are easy to see around Krafla Volcano, in the northeastern part of Iceland. Here, existing ground cracks have widened and new ones appear every few months. From 1975 to 1984, numerous episodes of rifting (surface cracking) took place along the Krafla fissure zone. Some of these rifting events were accompanied by volcanic activity; the ground would gradually rise 1-2 m before abruptly dropping, signalling an impending eruption. Between 1975 and 1984, the displacements caused by rifting totalled about 7 m.

In East Africa, spreading processes have already torn Saudi Arabia away from the rest of the African continent, forming the Red Sea. The actively splitting African Plate and the Arabian Plate meet in what geologists call a triple junction, where the Red Sea meets the Gulf of Aden. A new spreading center may be developing under Africa along the East African Rift Zone. When the continental crust stretches beyond its limits, tension cracks begin to appear on the Earth's surface. Magma rises and squeezes through the widening cracks, sometimes to erupt and form volcanoes. The rising magma, whether or not it erupts, puts more pressure on the crust to produce additional fractures and, ultimately, the rift zone.
```

### R1

```text
The Mid-Atlantic Ridge is described as one of the best-known divergent boundaries.

The Mid-Atlantic Ridge is one segment of the global mid-ocean ridge system.

Magma pushing up from the mantle creates new crust at spreading centers.

Seafloor spreading over millions of years has resulted in plate movement of thousands of kilometers.

Seafloor spreading caused the Atlantic Ocean to grow from a small inlet into its present vast ocean.

The consequences of plate movement include widening existing ground cracks and the appearance of new ones around Krafla Volcano.

The displacements at Krafla were caused by rifting.

Ground rise and abrupt dropping signalled an impending eruption.

Spreading processes tore Saudi Arabia away from the rest of Africa, forming the Red Sea.

When continental crust stretches beyond its limits, tension cracks appear on Earth's surface.

Rising magma puts more pressure on the crust.

Magma pressure produces additional fractures in the crust.

Crustal fractures contribute ultimately to the formation of a rift zone.

The spreading rate along the Mid-Atlantic Ridge averages about 2.5 centimeters per year, or 25 kilometers in a million years.

Iceland straddles the Mid-Atlantic Ridge and provides a natural laboratory for studying spreading processes on land.

Iceland is splitting along the spreading center between the North American and Eurasian Plates.

Numerous episodes of rifting took place along the Krafla fissure zone from 1975 to 1984.

Some rifting events were accompanied by volcanic activity.

The actively splitting African Plate and Arabian Plate meet at a triple junction where the Red Sea meets the Gulf of Aden.

A new spreading center may be developing under Africa along the East African Rift Zone.

Magma can squeeze through widening cracks and sometimes erupt to form volcanoes.

Newly formed oceanic crust is transported away from the ridge crest as plates move in opposite directions.

The consequences of plate movement are easy to see around Krafla Volcano, in the northeastern part of Iceland.

Explanatory dependencies:
Block 1 -> Block 2: The next block supplies an example of the preceding idea.
Block 2 -> Block 3: The next block establishes scale or timescale.
Block 3 -> Block 4: The next block grounds the explanation in evidence or observation.
Block 4 -> Block 5: The next block develops a consequence of the preceding material.
Block 5 -> Block 6: The next block establishes scale or timescale.
Block 6 -> Block 7: The explanation continues in source order.
```

### R2

```text
Divergent boundaries occur along spreading centers where plates are moving apart and new crust is created by magma pushing up from the mantle.

Picture two giant conveyor belts, facing each other but slowly moving in opposite directions as they transport newly formed oceanic crust away from the ridge crest.

Perhaps the best known of the divergent boundaries is the Mid-Atlantic Ridge.

This submerged mountain range, which extends from the Arctic Ocean to beyond the southern tip of Africa, is but one segment of the global mid-ocean ridge system that encircles the Earth.

The rate of spreading along the Mid-Atlantic Ridge averages about 2.5 centimeters per year (cm/yr), or 25 km in a million years.

This rate may seem slow by human standards, but because this process has been going on for millions of years, it has resulted in plate movement of thousands of kilometers.

Seafloor spreading over the past 100 to 200 million years has caused the Atlantic Ocean to grow from a tiny inlet of water between the continents of Europe, Africa, and the Americas into the vast ocean that exists today.

The volcanic country of Iceland, which straddles the Mid-Atlantic Ridge, offers scientists a natural laboratory for studying on land the processes also occurring along the submerged parts of a spreading ridge.

Iceland is splitting along the spreading center between the North American and Eurasian Plates, as North America moves westward relative to Eurasia.

The consequences of plate movement are easy to see around Krafla Volcano, in the northeastern part of Iceland.

Here, existing ground cracks have widened and new ones appear every few months.

From 1975 to 1984, numerous episodes of rifting (surface cracking) took place along the Krafla fissure zone.

Some of these rifting events were accompanied by volcanic activity; the ground would gradually rise 1-2 m before abruptly dropping, signalling an impending eruption.

Between 1975 and 1984, the displacements caused by rifting totalled about 7 m.

In East Africa, spreading processes have already torn Saudi Arabia away from the rest of the African continent, forming the Red Sea.

The actively splitting African Plate and the Arabian Plate meet in what geologists call a triple junction, where the Red Sea meets the Gulf of Aden.

A new spreading center may be developing under Africa along the East African Rift Zone.

When the continental crust stretches beyond its limits, tension cracks begin to appear on the Earth's surface.

Magma rises and squeezes through the widening cracks, sometimes to erupt and form volcanoes.

The rising magma, whether or not it erupts, puts more pressure on the crust to produce additional fractures and, ultimately, the rift zone.
```

### R3

```text
Spreading processes tore Saudi Arabia away from the rest of Africa, forming the Red Sea.
|
+-- Divergent boundaries occur along spreading centers where plates are moving apart and new crust is created by magma pushing up from the mantle.
+-- Picture two giant conveyor belts, facing each other but slowly moving in opposite directions as they transport newly formed oceanic crust away from the ridge crest.
+-- Perhaps the best known of the divergent boundaries is the Mid-Atlantic Ridge.
+-- This submerged mountain range, which extends from the Arctic Ocean to beyond the southern tip of Africa, is but one segment of the global mid-ocean ridge system that encircles the Earth.
+-- The rate of spreading along the Mid-Atlantic Ridge averages about 2.5 centimeters per year (cm/yr), or 25 km in a million years.
+-- This rate may seem slow by human standards, but because this process has been going on for millions of years, it has resulted in plate movement of thousands of kilometers.
+-- Seafloor spreading over the past 100 to 200 million years has caused the Atlantic Ocean to grow from a tiny inlet of water between the continents of Europe, Africa, and the Americas into the vast ocean that exists today.
+-- The volcanic country of Iceland, which straddles the Mid-Atlantic Ridge, offers scientists a natural laboratory for studying on land the processes also occurring along the submerged parts of a spreading ridge.
+-- Iceland is splitting along the spreading center between the North American and Eurasian Plates, as North America moves westward relative to Eurasia.
+-- The consequences of plate movement are easy to see around Krafla Volcano, in the northeastern part of Iceland.
+-- Here, existing ground cracks have widened and new ones appear every few months.
+-- In East Africa, spreading processes have already torn Saudi Arabia away from the rest of the African continent, forming the Red Sea.
+-- The actively splitting African Plate and the Arabian Plate meet in what geologists call a triple junction, where the Red Sea meets the Gulf of Aden.
+-- A new spreading center may be developing under Africa along the East African Rift Zone.
+-- When the continental crust stretches beyond its limits, tension cracks begin to appear on the Earth's surface.
+-- Magma rises and squeezes through the widening cracks, sometimes to erupt and form volcanoes.
+-- The rising magma, whether or not it erupts, puts more pressure on the crust to produce additional fractures and, ultimately, the rift zone.

The displacements at Krafla were caused by rifting.
|
+-- From 1975 to 1984, numerous episodes of rifting (surface cracking) took place along the Krafla fissure zone.
+-- Some of these rifting events were accompanied by volcanic activity; the ground would gradually rise 1-2 m before abruptly dropping, signalling an impending eruption.
+-- Between 1975 and 1984, the displacements caused by rifting totalled about 7 m.

Explanatory path (not a new causal assertion):
Block 1 --[EXEMPLIFIES]--> Block 2
Block 2 --[SCALES_TO]--> Block 3
Block 3 --[GROUNDS]--> Block 4
Block 4 --[LEADS_TO]--> Block 5
Block 5 --[SCALES_TO]--> Block 6
Block 6 --[CONTINUES]--> Block 7
```

[Exact recovery and audit packet](cases/01.json)
[Frozen authoritative substrate](substrates/01.json)

## 2. How did our Solar System form?

### R0

```text
Earth is the only world that we know of that has life. All of the plants and animals and microbes and other living things on Earth have evolved here. So, for us to understand where life as we know it came from, we need to understand where our planet came from.

The Sun and the planets and all of the other stuff in our solar system all formed from a really big cloud of gas and dust in space. We call such a cloud a “nebula” and more than one of them we refer to as “nebulae.” There are nebulae all around our galaxy, and it’s from these nebulae that stars and planets form. Nebulae are massive clouds of dust and debris in space and have all the ingredients to form stars and planets. When enough material is available, it begins to stick together forming a large mass. In time, the mass can grow large enough to form a planet or even a new star.

We currently think that our solar system formed from a large nebula, perhaps after the explosion of a nearby star. Some big stars can explode, something called a supernova, and that explosion has enough energy to make the gas and dust in nearby nebulae start swirling and spinning about. As this happened, it caused a lot of the material in the nebula to fall into its center, and that’s where the Sun started forming. Meanwhile, the rest of the gas and dust in the nebula began colliding and sticking together, making little pieces of metal and rock. Those small pieces then collided with each other, forming larger pieces, which then collided with each other to form even larger ones. These were young planets, and eventually, over a long time and through many, many collisions, our eight planets were formed – Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.

We call the pattern that the planets make when they go around the Sun an “orbit.” Well, when the planets were first forming from that cloud in space, the cloud itself was spinning in the same direction as the orbits of the planets today, with the Sun forming in the middle and also spinning in the same direction. That’s why we see the planets moving around the Sun the way that they do today!

You might also know that the Moon orbits around Earth. For something to be a moon, it needs to be in orbit around a planet. One thing that makes a planet is that a planet has to be orbiting a star. But star systems also have orbits. They orbit around their entire galaxy. So, orbits are really important for us to learn about if we want to know where we came from.
```

### R1

```text
Earth is the only world that we know of that has life. All of the plants and animals and microbes and other living things on Earth have evolved here. So, for us to understand where life as we know it came from, we need to understand where our planet came from.

The Sun and the planets and all of the other stuff in our solar system all formed from a really big cloud of gas and dust in space. We call such a cloud a “nebula” and more than one of them we refer to as “nebulae.” There are nebulae all around our galaxy, and it’s from these nebulae that stars and planets form. Nebulae are massive clouds of dust and debris in space and have all the ingredients to form stars and planets. When enough material is available, it begins to stick together forming a large mass. In time, the mass can grow large enough to form a planet or even a new star.

We currently think that our solar system formed from a large nebula, perhaps after the explosion of a nearby star. Some big stars can explode, something called a supernova, and that explosion has enough energy to make the gas and dust in nearby nebulae start swirling and spinning about. As this happened, it caused a lot of the material in the nebula to fall into its center, and that’s where the Sun started forming. Meanwhile, the rest of the gas and dust in the nebula began colliding and sticking together, making little pieces of metal and rock. Those small pieces then collided with each other, forming larger pieces, which then collided with each other to form even larger ones. These were young planets, and eventually, over a long time and through many, many collisions, our eight planets were formed – Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.

We call the pattern that the planets make when they go around the Sun an “orbit.” Well, when the planets were first forming from that cloud in space, the cloud itself was spinning in the same direction as the orbits of the planets today, with the Sun forming in the middle and also spinning in the same direction. That’s why we see the planets moving around the Sun the way that they do today!

You might also know that the Moon orbits around Earth. For something to be a moon, it needs to be in orbit around a planet. One thing that makes a planet is that a planet has to be orbiting a star. But star systems also have orbits. They orbit around their entire galaxy. So, orbits are really important for us to learn about if we want to know where we came from.
```

### R2

```text
Earth is the only world that we know of that has life.

All of the plants and animals and microbes and other living things on Earth have evolved here.

So, for us to understand where life as we know it came from, we need to understand where our planet came from.

The Sun and the planets and all of the other stuff in our solar system all formed from a really big cloud of gas and dust in space.

We call such a cloud a “nebula” and more than one of them we refer to as “nebulae.”

There are nebulae all around our galaxy, and it’s from these nebulae that stars and planets form.

Nebulae are massive clouds of dust and debris in space and have all the ingredients to form stars and planets.

When enough material is available, it begins to stick together forming a large mass.

In time, the mass can grow large enough to form a planet or even a new star.

We currently think that our solar system formed from a large nebula, perhaps after the explosion of a nearby star.

Some big stars can explode, something called a supernova, and that explosion has enough energy to make the gas and dust in nearby nebulae start swirling and spinning about.

As this happened, it caused a lot of the material in the nebula to fall into its center, and that’s where the Sun started forming.

Meanwhile, the rest of the gas and dust in the nebula began colliding and sticking together, making little pieces of metal and rock.

Those small pieces then collided with each other, forming larger pieces, which then collided with each other to form even larger ones.

These were young planets, and eventually, over a long time and through many, many collisions, our eight planets were formed – Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.

We call the pattern that the planets make when they go around the Sun an “orbit.”

Well, when the planets were first forming from that cloud in space, the cloud itself was spinning in the same direction as the orbits of the planets today, with the Sun forming in the middle and also spinning in the same direction.

That’s why we see the planets moving around the Sun the way that they do today!

You might also know that the Moon orbits around Earth.

For something to be a moon, it needs to be in orbit around a planet.

One thing that makes a planet is that a planet has to be orbiting a star.

But star systems also have orbits. They orbit around their entire galaxy.

So, orbits are really important for us to learn about if we want to know where we came from.
```

### R3

```text
A nebula is a cloud of gas and dust in space, and nebulae is the plural term.
|
+-- Earth is the only world that we know of that has life.
+-- All of the plants and animals and microbes and other living things on Earth have evolved here.
+-- So, for us to understand where life as we know it came from, we need to understand where our planet came from.
+-- The Sun and the planets and all of the other stuff in our solar system all formed from a really big cloud of gas and dust in space.
+-- We call such a cloud a “nebula” and more than one of them we refer to as “nebulae.”
+-- There are nebulae all around our galaxy, and it’s from these nebulae that stars and planets form.
+-- Nebulae are massive clouds of dust and debris in space and have all the ingredients to form stars and planets.
+-- When enough material is available, it begins to stick together forming a large mass.
+-- In time, the mass can grow large enough to form a planet or even a new star.
+-- We currently think that our solar system formed from a large nebula, perhaps after the explosion of a nearby star.
+-- Some big stars can explode, something called a supernova, and that explosion has enough energy to make the gas and dust in nearby nebulae start swirling and spinning about.
+-- As this happened, it caused a lot of the material in the nebula to fall into its center, and that’s where the Sun started forming.
+-- Meanwhile, the rest of the gas and dust in the nebula began colliding and sticking together, making little pieces of metal and rock.
+-- Those small pieces then collided with each other, forming larger pieces, which then collided with each other to form even larger ones.
+-- These were young planets, and eventually, over a long time and through many, many collisions, our eight planets were formed – Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.
+-- We call the pattern that the planets make when they go around the Sun an “orbit.”
+-- Well, when the planets were first forming from that cloud in space, the cloud itself was spinning in the same direction as the orbits of the planets today, with the Sun forming in the middle and also spinning in the same direction.
+-- That’s why we see the planets moving around the Sun the way that they do today!
+-- You might also know that the Moon orbits around Earth.
+-- For something to be a moon, it needs to be in orbit around a planet.
+-- One thing that makes a planet is that a planet has to be orbiting a star.
+-- But star systems also have orbits. They orbit around their entire galaxy.
+-- So, orbits are really important for us to learn about if we want to know where we came from.

Explanatory path (not a new causal assertion):
Block 1 --[CONTINUES]--> Block 2
Block 2 --[ELABORATES]--> Block 3
Block 3 --[QUALIFIES]--> Block 4
Block 4 --[QUALIFIES]--> Block 5
```

[Exact recovery and audit packet](cases/02.json)
[Frozen authoritative substrate](substrates/02.json)

## 3. What Is the Jet Stream?

### R0

```text
Jet streams are narrow bands of strong wind that generally blow from west to east all across the globe. Earth has four primary jet streams: two polar jet streams, near the north and south poles, and two subtropical jet streams closer to the equator.

Jet streams form when warm air masses meet cold air masses in the atmosphere.

The Sun doesn’t heat the whole Earth evenly. That’s why areas near the equator are hot and areas near the poles are cold.

So when Earth’s warmer air masses meet cooler air masses, the warmer air rises up higher in the atmosphere while cooler air sinks down to replace the warm air. This movement creates an air current, or wind. A jet stream is a type of air current that forms high in the atmosphere.

On average, jet streams move at about 110 miles per hour. But dramatic temperature differences between the warm and cool air masses can cause jet streams to move at much higher speeds — 250 miles per hour or faster. Speeds this high usually happen in polar jet streams in the winter time.

Jet streams are located about five to nine miles above Earth’s surface in the mid to upper troposphere — the layer of Earth’s atmosphere where we live and breathe.

Airplanes also fly in the mid to upper troposphere. So, if an airplane flies in a powerful jet stream and they are traveling in the same direction, the airplane can get a boost. That’s why an airplane flying a route from west to east can generally make the trip faster than an airplane traveling the same route east to west.

The fast-moving air currents in a jet stream can transport weather systems across the United States, affecting temperature and precipitation. However, if a weather system is far away from a jet stream, it might stay in one place, causing heat waves or floods.

Earth’s four primary jet streams only travel from west to east. Jet streams typically move storms and other weather systems from west to east. However, jet streams can move in different ways, creating bulges of winds to the north and south.

Storms tend to follow the edge of the jet stream, where the difference between cool and warm air creates the turbulent conditions for storms. The farther south the jet stream is pushed, the warmer and wetter the air will be where the colder Arctic air meets up with it. That makes for more thunder and lightning, and more tornadoes.
```

### R1

```text
Jet streams are narrow bands of strong wind that generally blow from west to east all across the globe. Earth has four primary jet streams: two polar jet streams, near the north and south poles, and two subtropical jet streams closer to the equator.

Jet streams form when warm air masses meet cold air masses in the atmosphere.

The Sun doesn’t heat the whole Earth evenly. That’s why areas near the equator are hot and areas near the poles are cold.

So when Earth’s warmer air masses meet cooler air masses, the warmer air rises up higher in the atmosphere while cooler air sinks down to replace the warm air. This movement creates an air current, or wind. A jet stream is a type of air current that forms high in the atmosphere.

On average, jet streams move at about 110 miles per hour. But dramatic temperature differences between the warm and cool air masses can cause jet streams to move at much higher speeds — 250 miles per hour or faster. Speeds this high usually happen in polar jet streams in the winter time.

Jet streams are located about five to nine miles above Earth’s surface in the mid to upper troposphere — the layer of Earth’s atmosphere where we live and breathe.

Airplanes also fly in the mid to upper troposphere. So, if an airplane flies in a powerful jet stream and they are traveling in the same direction, the airplane can get a boost. That’s why an airplane flying a route from west to east can generally make the trip faster than an airplane traveling the same route east to west.

The fast-moving air currents in a jet stream can transport weather systems across the United States, affecting temperature and precipitation. However, if a weather system is far away from a jet stream, it might stay in one place, causing heat waves or floods.

Earth’s four primary jet streams only travel from west to east. Jet streams typically move storms and other weather systems from west to east. However, jet streams can move in different ways, creating bulges of winds to the north and south.

Storms tend to follow the edge of the jet stream, where the difference between cool and warm air creates the turbulent conditions for storms. The farther south the jet stream is pushed, the warmer and wetter the air will be where the colder Arctic air meets up with it. That makes for more thunder and lightning, and more tornadoes.
```

### R2

```text
Jet streams are narrow bands of strong wind that generally blow from west to east all across the globe.

Earth has four primary jet streams: two polar jet streams, near the north and south poles, and two subtropical jet streams closer to the equator.

Jet streams form when warm air masses meet cold air masses in the atmosphere.

The Sun doesn’t heat the whole Earth evenly. That’s why areas near the equator are hot and areas near the poles are cold.

So when Earth’s warmer air masses meet cooler air masses, the warmer air rises up higher in the atmosphere while cooler air sinks down to replace the warm air. This movement creates an air current, or wind.

A jet stream is a type of air current that forms high in the atmosphere.

On average, jet streams move at about 110 miles per hour.

But dramatic temperature differences between the warm and cool air masses can cause jet streams to move at much higher speeds — 250 miles per hour or faster.

Speeds this high usually happen in polar jet streams in the winter time.

Jet streams are located about five to nine miles above Earth’s surface in the mid to upper troposphere — the layer of Earth’s atmosphere where we live and breathe.

Airplanes also fly in the mid to upper troposphere.

So, if an airplane flies in a powerful jet stream and they are traveling in the same direction, the airplane can get a boost.

That’s why an airplane flying a route from west to east can generally make the trip faster than an airplane traveling the same route east to west.

The fast-moving air currents in a jet stream can transport weather systems across the United States, affecting temperature and precipitation.

However, if a weather system is far away from a jet stream, it might stay in one place, causing heat waves or floods.

Earth’s four primary jet streams only travel from west to east.

Jet streams typically move storms and other weather systems from west to east.

However, jet streams can move in different ways, creating bulges of winds to the north and south.

Storms tend to follow the edge of the jet stream, where the difference between cool and warm air creates the turbulent conditions for storms. The farther south the jet stream is pushed, the warmer and wetter the air will be where the colder Arctic air meets up with it.

That makes for more thunder and lightning, and more tornadoes.
```

### R3

```text
Uneven solar heating produces warmer equatorial areas and colder polar areas, creating a temperature difference.
|
+-- Jet streams are narrow bands of strong wind that generally blow from west to east all across the globe.
+-- Earth has four primary jet streams: two polar jet streams, near the north and south poles, and two subtropical jet streams closer to the equator.
+-- Jet streams form when warm air masses meet cold air masses in the atmosphere.
+-- The Sun doesn’t heat the whole Earth evenly. That’s why areas near the equator are hot and areas near the poles are cold.
+-- So when Earth’s warmer air masses meet cooler air masses, the warmer air rises up higher in the atmosphere while cooler air sinks down to replace the warm air. This movement creates an air current, or wind.
+-- A jet stream is a type of air current that forms high in the atmosphere.
+-- On average, jet streams move at about 110 miles per hour.
+-- But dramatic temperature differences between the warm and cool air masses can cause jet streams to move at much higher speeds — 250 miles per hour or faster.
+-- Speeds this high usually happen in polar jet streams in the winter time.
+-- Jet streams are located about five to nine miles above Earth’s surface in the mid to upper troposphere — the layer of Earth’s atmosphere where we live and breathe.
+-- Airplanes also fly in the mid to upper troposphere.
+-- So, if an airplane flies in a powerful jet stream and they are traveling in the same direction, the airplane can get a boost.
+-- That’s why an airplane flying a route from west to east can generally make the trip faster than an airplane traveling the same route east to west.
+-- The fast-moving air currents in a jet stream can transport weather systems across the United States, affecting temperature and precipitation.
+-- However, if a weather system is far away from a jet stream, it might stay in one place, causing heat waves or floods.
+-- Earth’s four primary jet streams only travel from west to east.
+-- Jet streams typically move storms and other weather systems from west to east.
+-- Storms tend to follow the edge of the jet stream, where the difference between cool and warm air creates the turbulent conditions for storms. The farther south the jet stream is pushed, the warmer and wetter the air will be where the colder Arctic air meets up with it.
+-- That makes for more thunder and lightning, and more tornadoes.

Jet streams can create bulges of winds to the north and south.
|
+-- However, jet streams can move in different ways, creating bulges of winds to the north and south.

Explanatory path (not a new causal assertion):
Block 1 --[ELABORATES]--> Block 2
Block 2 --[ELABORATES]--> Block 3
Block 3 --[SCALES_TO]--> Block 4
Block 4 --[QUALIFIES]--> Block 5
Block 5 --[QUALIFIES]--> Block 6
Block 6 --[EXEMPLIFIES]--> Block 7
Block 7 --[LEADS_TO]--> Block 8
Block 8 --[CONTRASTS_WITH]--> Block 9
Block 9 --[QUALIFIES]--> Block 10
Block 10 --[CONTRASTS_WITH]--> Block 11
Block 11 --[CONTINUES]--> Block 12
```

[Exact recovery and audit packet](cases/03.json)
[Frozen authoritative substrate](substrates/03.json)

## Review questions

1. Does R1 reduce reading cost without changing the knowledge?
2. Does R2 synthesize overlapping assertions rather than merely reduce sentence count?
3. Does R3 explain membership through higher-order principles, or merely group units?
4. Does the architecture reduce reconstruction work?
5. Can every qualification, dependency, implication, and item be recovered exactly?
6. Does the plain text expose the compiler's limits?

The deterministic finding does not authorize a provider call. Any bounded model candidate requires a separately approved contract.
