shard_value_0 = 50
shard_value_1 = 65
shard_value_2 = 85
shard_value_3 = 150
shard_value_4 = 195
shard_value_5 = 235
shard_value_6 = 270
shard_value_7 = 300
xp_value_0 = 720
xp_value_1 = 900
xp_value_2 = 1200
xp_value_3 = 2100
xp_value_4 = 2700
xp_value_5 = 3300
xp_value_6 = 3750
xp_value_7 = 4200

required_levels = 0

current_level = int(input("Current level: "))
current_xp = int(input("Current XP: "))
current_shards = int(input("Current number Iridescent Shards: "))
shards_needed = int(input("Total number of Iridescent Shards needed: "))

total_shards_needed = shards_needed - current_shards

while current_shards <= shards_needed:
    if current_level == 100:
        current_level = 1

    if current_level <= 2:
        current_shards += shard_value_0
    elif current_level <= 3:
        current_shards += shard_value_1
    elif current_level <= 6:
        current_shards += shard_value_2
    elif current_level <= 14:
        current_shards += shard_value_3
    elif current_level <= 24:
        current_shards += shard_value_4
    elif current_level <= 34:
        current_shards += shard_value_5
    elif current_level <= 49:
        current_shards += shard_value_6
    elif current_level <= 99:
        current_shards += shard_value_7
    
    current_level += 1
    required_levels += 1

print(f"Levels needed: {required_levels}. Total Iridescent Shards needed: {total_shards_needed}.")