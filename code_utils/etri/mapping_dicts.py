action_option_mapping = {
    111: "Sleep",
    112: "Sleepless",
    121: "Meal",
    122: "Snack",
    131: "Medical services, treatments, sick rest",
    132: "Personal hygiene (bath)",
    133: "Appearance management (makeup, change of clothes)",
    134: "Beauty-related services",
    211: "Main job",
    212: "Side job",
    213: "Rest during work",
    22: "Job search",
    311: "School class / seminar (listening)",
    312: "Break between classes",
    313: "School homework, self-study (individual)",
    314: "Team project (in groups)",
    321: "Private tutoring (offline)",
    322: "Online courses",
    41: "Preparing food and washing dishes",
    42: "Laundry and ironing",
    43: "Housing management and cleaning",
    44: "Vehicle management",
    45: "Pet and plant caring",
    46: "Purchasing goods and services (grocery/take-out)",
    51: "Caring for children under 10 who live together",
    52: "Caring for elementary, middle, and high school students over 10 who live together",
    53: "Caring for a spouse",
    54: "Caring for parents and grandparents who live together",
    55: "Caring for other family members who live together",
    56: "Caring for parents and grandparents who do not live together",
    57: "Caring for other family members who do not live together",
    81: "Personal care-related travel",
    82: "Commuting and work-related travel",
    83: "Education-related travel",
    84: "Travel related to housing management",
    85: "Travel related to caring for family and household members",
    86: "Travel related to participation and volunteering",
    87: "Socializing and leisure-related travel",
    61: "Religious activities",
    62: "Political activity",
    63: "Ceremonial activities",
    64: "Volunteer",
    711: "Offline communication",
    712: "Video or voice call",
    713: "Text or email (Online)",
    721: "Reading books, newspapers, and magazines",
    722: "Watching TV or video",
    723: "Listening to audio",
    724: "Internet search or blogging",
    725: "Gaming (mobile, computer, video)",
    741: "Watching a sporting event",
    742: "Watching movie",
    743: "Concerts and plays",
    744: "Art galleries and museums",  # NOTE: key repeated
    # 744: "Amusement Park, zoo",  # NOTE: key repeated
    745: "Festival, carnival",
    746: "Driving, sightseeing, excursion",
    751: "Walking",
    752: "Running, jogging",
    753: "Climbing, hiking",
    754: "Biking",
    755: "Ball games (soccer, basketball, baseball, tennis, etc)",
    756: "Personal exercises (yoga, pilates, etc.)",  # NOTE: key repeated
    # 756: "Camping, fishing",  # NOTE: key repeated
    761: "Group games (board games, card games, puzzles, etc.)",
    762: "Personal hobbies (woodworking, gardening, etc.)",
    763: "Group performances (orchestra, choir, troupe, etc.)",
    764: "Liberal arts and learning (languages, musical instruments, etc.)",
    791: "Nightlife",
    792: "Smoking",
    793: "Do nothing and rest",
    91: "Online shopping",
    92: "Offline shopping",
}

action_sub_option_mapping = {
    "meal_amount": {
        1: "Light",
        2: "Moderate",
        3: "Heavy",
    },
    "move_method": {
        1: "Walk",
        2: "Driving",
        3: "Taxi, passenger",
        4: "Personal mobility",
        5: "Bus",
        6: "Train, subway",
        7: "Others",
    },
}

condition_sub1_option_mapping = {
    1: "With family",
    2: "With friends",
    3: "With colleagues",
    4: "With acquaintances",
    5: "With others",
}

# 1 (passive in conversation)
# 2 (moderate participation in conversation)
# 3 (active in conversation)
condition_sub2_option_mapping = {
    1: "Passive in conversation",
    2: "Moderate participation in conversation",
    3: "Active in conversation",
}

# (negative) 1-2-3-4-5-6-7 (positive)
# (relaxed) 1-2-3-4-5-6-7 (aroused)
# NOTE: Values in the activity column represent the detected activity of the mobile
# device using Google's Awareness API.
# Reference: https://developers.google.com/android/reference/com/google/android/gms/location/DetectedActivity?hl=en
activity_mapping = {
    0: "In vehicle",
    1: "On bicycle",
    2: "On foot",
    3: "Still",
    4: "Unknown",
    5: "Tilting",
    7: "Walking",
    8: "Running",
}
