def tune_to_target_level(debugConsoleController):
    target_level = input("Enter target level: ")
    current_level = input("Enter current level: ")
    debugConsoleController.tune_to_target_level(int(target_level), int(current_level))
