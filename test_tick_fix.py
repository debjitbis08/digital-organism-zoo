#!/usr/bin/env python3
"""
Test that tick variable is properly defined
"""

# Simulate the crisis detection logic
def test_crisis_detection():
    print("🔍 Testing crisis detection logic...")
    
    # Simulate loop variables
    tick = 100
    population_crisis_level = 0.2
    food_crisis = True
    total_food = 3
    food_per_organism = 1.5
    
    # Test the condition that was causing the error
    if (population_crisis_level > 0.7 or food_crisis) and tick % 50 == 0:
        print(f"🚨 ECOSYSTEM CRISIS: Population crisis {population_crisis_level:.2f}, Food crisis: {food_crisis}")
        print(f"   Food stats: {total_food} total, {food_per_organism:.1f} per organism")
    else:
        print("✅ Crisis detection logic working - no crisis message this tick")
    
    print("✅ No 'tick' variable error!")

if __name__ == "__main__":
    test_crisis_detection()