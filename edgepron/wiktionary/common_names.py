"""Curated sets of the most common English given names and surnames.

Culled from the dictionary (ticket 17) because any English TTS already says
these correctly, and an explicit respelling risks making them worse.

Hand-curated from well-known "most common English names" rankings. Given names
are culled broadly (Sophia/﻿Alexander/Greta are easy for a TTS); surnames are
restricted to *English-origin* names only, because common non-English surnames
(Nguyen, Garcia, Patel, Kim…) are exactly the foreign words a TTS gets wrong and
must NOT be culled.
"""

COMMON_GIVEN_NAMES = frozenset({
    # male
    "james", "john", "robert", "michael", "william", "david", "richard", "joseph",
    "thomas", "charles", "christopher", "daniel", "matthew", "anthony", "mark",
    "donald", "steven", "paul", "andrew", "joshua", "kenneth", "kevin", "brian",
    "george", "timothy", "ronald", "edward", "jason", "jeffrey", "ryan", "jacob",
    "gary", "nicholas", "eric", "jonathan", "stephen", "larry", "justin", "scott",
    "brandon", "benjamin", "samuel", "gregory", "alexander", "frank", "patrick",
    "jack", "dennis", "jerry", "tyler", "aaron", "jose", "adam", "henry", "nathan",
    "douglas", "zachary", "peter", "kyle", "walter", "ethan", "jeremy", "harold",
    "keith", "christian", "roger", "noah", "gerald", "carl", "terry", "sean", "austin",
    "arthur", "lawrence", "jesse", "dylan", "bryan", "joe", "jordan", "billy", "bruce",
    "albert", "willie", "gabriel", "logan", "alan", "juan", "wayne", "roy", "ralph",
    "randy", "eugene", "vincent", "russell", "elijah", "louis", "bobby", "philip",
    "johnny", "martin", "fred", "bradley", "trevor", "stanley", "leonard", "dale",
    "marcus", "tracey", "dean", "brendan", "conor", "aidan", "kieran",
    # female
    "mary", "patricia", "jennifer", "linda", "elizabeth", "barbara", "susan",
    "jessica", "sarah", "karen", "nancy", "lisa", "margaret", "betty", "sandra",
    "ashley", "kimberly", "emily", "donna", "michelle", "dorothy", "carol", "amanda",
    "melissa", "deborah", "stephanie", "rebecca", "sharon", "laura", "cynthia",
    "kathleen", "amy", "shirley", "angela", "helen", "anna", "brenda", "pamela",
    "nicole", "emma", "samantha", "katherine", "christine", "debra", "rachel",
    "carolyn", "janet", "catherine", "maria", "heather", "diane", "ruth", "julie",
    "olivia", "joyce", "virginia", "victoria", "kelly", "lauren", "christina", "joan",
    "evelyn", "judith", "megan", "cheryl", "andrea", "hannah", "martha", "jacqueline",
    "frances", "gloria", "ann", "teresa", "kathryn", "sara", "janice", "jean", "alice",
    "madison", "doris", "julia", "judy", "grace", "denise", "amber", "marilyn",
    "beverly", "danielle", "theresa", "sophia", "greta", "georgia", "kate", "lucy",
    "charlotte", "molly", "katie", "emily", "hannah", "abigail", "isabella", "mia",
})

COMMON_SURNAMES = frozenset({
    # English-origin surnames only (see module docstring)
    "smith", "johnson", "williams", "brown", "jones", "miller", "davis", "wilson",
    "anderson", "thomas", "taylor", "moore", "jackson", "martin", "lee", "thompson",
    "white", "harris", "clark", "lewis", "robinson", "walker", "young", "allen",
    "king", "wright", "scott", "hill", "green", "adams", "nelson", "baker", "hall",
    "campbell", "mitchell", "carter", "roberts", "phillips", "evans", "turner",
    "parker", "edwards", "collins", "stewart", "morris", "murphy", "cook", "rogers",
    "morgan", "cooper", "peterson", "bailey", "reed", "kelly", "howard", "cox",
    "ward", "richardson", "watson", "brooks", "wood", "james", "bennett", "gray",
    "hughes", "price", "long", "ross", "foster", "powell", "jenkins", "perry",
    "russell", "sullivan", "bell", "coleman", "butler", "henderson", "barnes",
    "fisher", "simmons", "patterson", "alexander", "hamilton", "graham", "reynolds",
    "griffin", "wallace", "west", "cole", "hayes", "bryant", "kent", "snyder",
    "marshall", "burns", "armstrong", "kennedy", "harvey", "wells", "gibson",
    "ellis", "mcdonald", "murray", "owens", "dixon", "porter", "lane", "ray",
    "hudson", "harrison", "stanley", "gordon", "mason", "hunter", "perkins",
})

COMMON_NAMES = COMMON_GIVEN_NAMES | COMMON_SURNAMES

__all__ = ["COMMON_GIVEN_NAMES", "COMMON_SURNAMES", "COMMON_NAMES"]