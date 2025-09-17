import random

# Define coin sides
coin_sides = ['H', 'T']

# Dictionary to store results
results_count = {
    'HH': 0,
    'HT': 0,
    'TH': 0,
    'TT': 0
}

# Simulate 40 tosses
for toss in range(1, 41):
    coin1 = random.choice(coin_sides)
    coin2 = random.choice(coin_sides)
    result = coin1 + coin2
    results_count[result] += 1
    print(f"Toss {toss}: {result}")

# Display summary
print("\nSummary of Results:")
for combo, count in results_count.items():
    print(f"{combo}: {count} times")
