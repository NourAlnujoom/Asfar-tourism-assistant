from app import add_site, init_database, add_sensor_data, delete_site, clear_sites_table

init_database()

lesser_known_sites = [
    ("Jabal al-Qalaa", "Historical Site", "Ancient citadel in Amman with Roman ruins and panoramic city views."),
    ("Shobak Castle", "Historical Site", "Crusader castle with tunnels and stone walls in the mountains of Shobak."),
    ("Ajloun Forest Reserve", "Nature Reserve", "Lush reserve with hiking trails and cabins, perfect for nature lovers."),
    ("Palm Village Restaurant", "Food Spot", "Local food spot with scenic views and traditional dishes."),
    ("O2 View", "Café", "Modern coffee house in Amman popular among youth for studying and hanging out."),
    ("Jordan National Gallery of Fine Art", "Art Space", "Hidden gallery with rotating exhibitions from local and regional artists."),
    ("BAN COFFEE HOUSE", "Café", "Cozy café in Amman with a relaxed vibe and artisanal drinks."),
    #("Al Ma'wa for Nature and Wildlife", "Wildlife Sanctuary", "Wildlife sanctuary near Jerash offering shelter to rescued animals."),
    ("Umm Qais", "Historical Site", "Roman ruins with views of the Sea of Galilee and Golan Heights."),
    #("Dana", "Cultural Village", "A traditional village on a cliff offering guesthouses and local crafts."),
    ("Jordan Museum", "Museum", "National museum featuring artifacts like the Dead Sea Scrolls."),
    ("Blooming Brothers Coffee Co", "Café", "Boutique flower shop café known for coffee and stunning floral design."),
    ("Padova Italian Cuisine", "Restaurant", "Italian-Jordanian fusion restaurant with cozy ambiance in Amman."),
    ("ALMOND COFFEE HOUSE - 8th circle", "Café", "Elegant café with artisanal pastries and a minimalist design."),
    ("The Duke's Diwan", "Cultural Spot", "1920s historic house in Amman preserved as a cultural experience."),
    ("Beit Sitti", "Cultural Experience", "Cooking school offering traditional Jordanian meals in a family setting."),
    ("Wild Jordan Center", "Eco Center", "Eco café/shop with views of Amman, supporting local nature reserves."),
    ("Dar Al-Anda Art Gallery", "Art Gallery", "Gallery in Jabal Lweibdeh showcasing Middle Eastern contemporary art."),
    ("Jadal for Knowledge & Culture", "Community Space", "Community space for music, talks, and social change in Amman."),
    ("Mlabbas - T-shirts & Gifts", "Shopping", "Concept store in Amman with pop-culture-inspired clothing and gifts."),
]
'''people_count = []'''
'''
people_count = [
    ("2025-08-07", "13:00", "Ajloun Forest Reserve", 23),
    ("2025-08-07", "14:00", "Umm Qais", 17),
    # Add more rows here
]
'''
clear_sites_table()
for name, category, desc in lesser_known_sites:
    success, msg = add_site(name, category, desc)
    print(f'{name} : {msg}')

'''
for date, hour, site_name, count in people_count:
    success,msg = add_sensor_data(date, hour, site_name, count)
    print(f'count in {site_name} on {date} at {hour}: {count}, message: {msg}')'''