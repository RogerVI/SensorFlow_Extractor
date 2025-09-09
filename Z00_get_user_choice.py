

from config_handler import load_config, save_config, project_reuse_flags

def get_user_choice(prompt, options):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    choice = -1
    while choice < 1 or choice > len(options):
        try:
            choice = int(input("Enter your choice: "))
            if choice < 1 or choice > len(options):
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    return choice - 1  # 🔁 On ne sauvegarde rien ici


# def get_user_choice(prompt, options):
#     """
#     Displays a prompt and a list of options, then gets and validates user input.

#     Args:
#         prompt (str): The message to display to the user.
#         options (list): A list of options to choose from.

#     Returns:
#         int: The index of the selected option (0-based).
#     """
#     print(prompt)
#     for i, option in enumerate(options, 1):
#         print(f"{i}. {option}")

#     choice = -1
#     while choice < 1 or choice > len(options):
#         try:
#             choice = int(input("Enter your choice: ")) #if choice isn't an int, send an error
#             if choice < 1 or choice > len(options):
#                 print("Invalid choice. Please try again.")
#         except ValueError:
#             print("Invalid input. Please enter a number.")

#     return choice - 1 #-1 to get a python index


import config_handler
import hashlib

def get_multiple_user_choices(prompt, options, project_key=None, key_name=None):
    config = config_handler.load_config()
    scope_key = project_key if project_key else "global"
    scope = config.setdefault(scope_key, {})

    raw_key = f"{scope_key}::{prompt}"
    config_key = key_name or f"choice_{hashlib.md5(raw_key.encode()).hexdigest()}"

    reuse_flag = config_handler.project_reuse_flags.get(scope_key, None)

    if config_key in scope:
        saved_choices = scope[config_key]

        if reuse_flag is None:
            print(prompt)
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("Saved selection:", ", ".join(saved_choices))
            reuse = input("Do you want to reuse this selection? (y/n): ").strip().lower()
            reuse_flag = (reuse == "y")
            config_handler.project_reuse_flags[scope_key] = reuse_flag

        if reuse_flag:
            print("✅ Reusing saved selection:", ", ".join(saved_choices))
            return saved_choices

    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        input_str = input("Enter your choices (e.g., 1, 3-5, all): ").strip().lower()

        if input_str in ("all", "everything"):
            print("You selected: all options")
            scope[config_key] = options.copy()
            config[scope_key] = scope
            config_handler.save_config(config)
            return options.copy()

        selected_indices = set()
        skipped_entries = []

        for part in input_str.split(","):
            part = part.strip()
            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    if start > end:
                        start, end = end, start
                    selected_indices.update(range(start, end + 1))
                except Exception:
                    skipped_entries.append(part)
            elif part.isdigit():
                selected_indices.add(int(part))
            else:
                skipped_entries.append(part)

        valid = [i for i in selected_indices if 1 <= i <= len(options)]
        invalid = [i for i in selected_indices if not (1 <= i <= len(options))]

        if skipped_entries or invalid:
            print("⚠️ Skipped invalid entries:", ", ".join(map(str, skipped_entries + invalid)))

        if valid:
            result = [options[i - 1] for i in sorted(valid)]
            print("You selected:", ", ".join(result))
            scope[config_key] = result
            config[scope_key] = scope
            config_handler.save_config(config)
            return result
        else:
            print("❌ No valid choices detected. Please try again.")




# from config_handler import load_config, save_config
# import hashlib

# _user_accepts_saved = None  # Ask only once

# def _generate_config_key(prompt):
#     # Generate a unique, stable key from the prompt text
#     return f"choice_{hashlib.md5(prompt.encode()).hexdigest()}"

# def get_multiple_user_choices(prompt, options):
#     global _user_accepts_saved

#     config_key = _generate_config_key(prompt)
#     config = load_config()

#     # If saved choices exist, ask once if the user wants to reuse them
#     if config_key in config:
#         saved_choices = config[config_key]

#         if _user_accepts_saved is None:
#             print(prompt)
#             for i, option in enumerate(options, 1):
#                 print(f"{i}. {option}")
#             print("Previously saved selection:", ", ".join(saved_choices))
#             reuse = input("Do you want to reuse this selection? (y/n): ").strip().lower()
#             _user_accepts_saved = (reuse == "y")

#         if _user_accepts_saved:
#             print("✅ Reusing saved selection:", ", ".join(saved_choices))
#             return saved_choices

#     # No saved config, or user chose not to reuse — ask normally
#     print(prompt)
#     for i, option in enumerate(options, 1):
#         print(f"{i}. {option}")

#     while True:
#         input_str = input("Enter your choices (e.g., 1, 3-5, all): ").strip().lower()

#         if input_str in ("all", "everything"):
#             print("You have selected: all options")
#             config[config_key] = options.copy()
#             save_config(config)
#             return options.copy()

#         selected_indices = set()
#         skipped_entries = []

#         parts = input_str.split(",")

#         for part in parts:
#             part = part.strip()
#             if "-" in part:
#                 try:
#                     start, end = map(int, part.split("-"))
#                     if start > end:
#                         start, end = end, start
#                     selected_indices.update(range(start, end + 1))
#                 except Exception:
#                     skipped_entries.append(part)
#             elif part.isdigit():
#                 selected_indices.add(int(part))
#             else:
#                 skipped_entries.append(part)

#         valid_indices = [i for i in selected_indices if 1 <= i <= len(options)]
#         invalid_indices = [i for i in selected_indices if not (1 <= i <= len(options))]

#         if skipped_entries or invalid_indices:
#             print("⚠️ Skipped invalid entries:", ", ".join(map(str, skipped_entries + invalid_indices)))

#         if valid_indices:
#             selected_options = [options[i - 1] for i in sorted(valid_indices)]
#             print("You have selected:", ", ".join(selected_options))
#             config[config_key] = selected_options
#             save_config(config)
#             return selected_options
#         else:
#             print("❌ No valid choices detected. Please try again.")



# # from config_handler import load_config, save_config

# # _user_accepts_saved = None  # pour mémoire unique à cette fonction

# # def get_multiple_user_choices(prompt, options, config_key="sensor_types"):
# #     global _user_accepts_saved

# #     config = load_config()

# #     # If a config already exist
# #     if config_key in config:
# #         saved_choices = config[config_key]

# #         # Don't repeat the question
# #         if _user_accepts_saved is None:
# #             print(prompt)
# #             for i, option in enumerate(options, 1):
# #                 print(f"{i}. {option}")

# #             print("📦 Previous registered selections :", ", ".join(saved_choices))
# #             reuse = input("Would you like to reuse this selection ? (y/n) : ").strip().lower()
# #             _user_accepts_saved = (reuse == "y")

# #         if _user_accepts_saved:
# #             print("✅ Previous selections reused :", ", ".join(saved_choices))
# #             return saved_choices

# #     # Otherwise, we follow the normal mode
# #     print(prompt)
# #     for i, option in enumerate(options, 1):
# #         print(f"{i}. {option}")

# #     while True:
# #         input_str = input("Enter your choices (e.g., 1, 3-5, all): ").strip().lower()

# #         if input_str in ("all", "tout"):
# #             print("You have selected: all options")
# #             config[config_key] = options.copy()
# #             save_config(config)
# #             return options.copy()

# #         selected_indices = set()
# #         skipped_entries = []

# #         parts = input_str.split(",")

# #         for part in parts:
# #             part = part.strip()
# #             if "-" in part:
# #                 try:
# #                     start, end = map(int, part.split("-"))
# #                     if start > end:
# #                         start, end = end, start
# #                     selected_indices.update(range(start, end + 1))
# #                 except Exception:
# #                     skipped_entries.append(part)
# #             elif part.isdigit():
# #                 selected_indices.add(int(part))
# #             else:
# #                 skipped_entries.append(part)

# #         valid_indices = [i for i in selected_indices if 1 <= i <= len(options)]
# #         invalid_indices = [i for i in selected_indices if not (1 <= i <= len(options))]

# #         if skipped_entries or invalid_indices:
# #             print("⚠️ Skipped invalid entries:", ", ".join(map(str, skipped_entries + invalid_indices)))

# #         if valid_indices:
# #             selected_options = [options[i - 1] for i in sorted(valid_indices)]
# #             print("You have selected:", ", ".join(selected_options))
# #             config[config_key] = selected_options
# #             save_config(config)
# #             return selected_options
# #         else:
# #             print("❌ No valid choices detected. Please try again.")





# def get_multiple_user_choices(prompt, options):
#     """
#     Displays a prompt and a list of options, then collects and validates multiple user inputs.
#     - Accepts ranges like 1-3
#     - Accepts "all" or "tout" to select everything
#     - Ignores extra spaces
#     - Tolerates errors (skips invalid entries but keeps valid ones)
#     - Displays a summary of selected choices
#     """
#     print(prompt)
#     for i, option in enumerate(options, 1):
#         print(f"{i}. {option}")

#     while True:
#         input_str = input("Enter your choices (e.g., 1, 3-5, all): ").strip().lower()

#         if input_str in ("all", "tout"):
#             print("You have selected: all options")
#             return options.copy()

#         selected_indices = set()
#         skipped_entries = []

#         parts = input_str.split(",")

#         for part in parts:
#             part = part.strip()
#             if "-" in part:
#                 try:
#                     start, end = map(int, part.split("-"))
#                     if start > end:
#                         start, end = end, start
#                     selected_indices.update(range(start, end + 1))
#                 except Exception:
#                     skipped_entries.append(part)
#             elif part.isdigit():
#                 selected_indices.add(int(part))
#             else:
#                 skipped_entries.append(part)

#         valid_indices = [i for i in selected_indices if 1 <= i <= len(options)]
#         invalid_indices = [i for i in selected_indices if not (1 <= i <= len(options))]

#         if skipped_entries or invalid_indices:
#             print("⚠️ Skipped invalid entries:", ", ".join(map(str, skipped_entries + invalid_indices)))

#         if valid_indices:
#             selected_options = [options[i - 1] for i in sorted(valid_indices)]
#             print("You have selected:", ", ".join(selected_options))
#             return selected_options
#         else:
#             print("❌ No valid choices detected. Please try again.")
