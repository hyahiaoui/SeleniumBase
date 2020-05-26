"""
Translates a SeleniumBase Python file into a different language

Usage:
        seleniumbase translate [SB_FILE].py [LANGUAGE] [ACTION]
        OR:    sbase translate [SB_FILE].py [LANGUAGE] [ACTION]
Languages:
        --en / --English    |    --zh / --Chinese
        --nl / --Dutch      |    --fr / --French
        --it / --Italian    |    --ja / --Japanese
        --ko / --Korean     |    --pt / --Portuguese
        --ru / --Russian    |    --es / --Spanish
Actions:
        -p / --print  (Print translation output to the screen)
        -o / --overwrite  (Overwrite the file being translated)
        -c / --copy  (Copy the translation to a new .py file)
Output:
        Translates a SeleniumBase Python file into the language
        specified. Method calls and "import" lines get swapped.
        Both a language and an action must be specified.
        The "-p" action can be paired with one other action.
        When running with "-c" (or "--copy"), the new file name
        will be the orginal name appended with an underscore
        plus the 2-letter language code of the new language.
        (Example: Translating "test_1.py" into Japanese with
        "-c" will create a new file called "test_1_ja.py".)
"""

import codecs
import colorama
import re
import sys
from seleniumbase.translate import master_dict

MD_F = master_dict.MD_F
MD_L_Codes = master_dict.MD_L_Codes
MD = master_dict.MD


def invalid_run_command(msg=None):
    exp = "  ** translate **\n\n"
    exp += "  Usage:\n"
    exp += "         seleniumbase translate [SB_FILE].py [LANGUAGE] [ACTION]\n"
    exp += "         OR:    sbase translate [SB_FILE].py [LANGUAGE] [ACTION]\n"
    exp += "  Languages:\n"
    exp += "         --en / --English    |    --zh / --Chinese\n"
    exp += "         --nl / --Dutch      |    --fr / --French\n"
    exp += "         --it / --Italian    |    --ja / --Japanese\n"
    exp += "         --ko / --Korean     |    --pt / --Portuguese\n"
    exp += "         --ru / --Russian    |    --es / --Spanish\n"
    exp += "  Actions:\n"
    exp += "         -p / --print  (Print translation output to the screen)\n"
    exp += "         -o / --overwrite  (Overwrite the file being translated)\n"
    exp += "         -c / --copy  (Copy the translation to a new .py file)\n"
    exp += "  Output:\n"
    exp += "         Translates a SeleniumBase Python file into the language\n"
    exp += '         specified. Method calls and "import" lines get swapped.\n'
    exp += "         Both a language and an action must be specified.\n"
    exp += '         The "-p" action can be paired with one other action.\n'
    exp += '         When running with "-c" (or "--copy"), the new file name\n'
    exp += "         will be the orginal name appended with an underscore\n"
    exp += "         plus the 2-letter language code of the new language.\n"
    exp += '         (Example: Translating "test_1.py" into Japanese with\n'
    exp += '          "-c" will create a new file called "test_1_ja.py".)\n'
    if not msg:
        raise Exception("INVALID RUN COMMAND!\n\n%s" % exp)
    else:
        raise Exception("INVALID RUN COMMAND!\n%s\n\n%s" % (msg, exp))


def process_test_file(code_lines, new_lang):
    detected_lang = None
    changed = False
    seleniumbase_lines = []
    lang_codes = MD_L_Codes.lang
    nl_code = lang_codes[new_lang]  # new_lang language code
    dl_code = None  # detected_lang language code
    md = MD.md  # Master Dictionary

    for line in code_lines:
        line = line.rstrip()

        # Find imports that determine the language
        if line.lstrip().startswith("from seleniumbase") and "import" in line:
            added_line = False
            for lang in MD_F.get_languages_list():
                data = re.match(r"^\s*" + MD_F.get_import_line(lang) + r"([\S\s]*)$", line)
                if data:
                    comments = "%s" % data.group(1)
                    new_line = None
                    detected_lang = lang
                    dl_code = lang_codes[detected_lang]
                    if detected_lang != new_lang:
                        changed = True
                        new_line = MD_F.get_import_line(new_lang) + comments
                    else:
                        new_line = line
                    if new_line.endswith("  # noqa"):  # Remove flake8 skip
                        new_line = new_line[0 : -len("  # noqa")]
                    seleniumbase_lines.append(new_line)
                    added_line = True
                    break
                data = re.match(r"^\s*" + MD_F.get_mqa_im_line(lang) + r"([\S\s]*)$", line)
                if data:
                    comments = "%s" % data.group(1)
                    new_line = None
                    detected_lang = lang
                    dl_code = lang_codes[detected_lang]
                    if detected_lang != new_lang:
                        changed = True
                        new_line = MD_F.get_mqa_im_line(new_lang) + comments
                    else:
                        new_line = line
                    if new_line.endswith("  # noqa"):  # Remove flake8 skip
                        new_line = new_line[0 : -len("  # noqa")]
                    seleniumbase_lines.append(new_line)
                    added_line = True
                    break
            if not added_line:
                # Probably a language missing from the translator.
                # Add the import line as it is and move on.
                seleniumbase_lines.append(line)
            continue

        # Find class definitions that determine the language
        if line.lstrip().startswith("class ") and ":" in line:
            added_line = False
            data = re.match(r"""^(\s*)class\s+([\S]+)\(([\S]+)\):([\S\s]*)$""", line)
            if data:
                whitespace = data.group(1)
                name = "%s" % data.group(2)
                parent_class = "%s" % data.group(3)
                comments = "%s" % data.group(4)
                if parent_class in MD_F.get_parent_classes_list():
                    detected_lang = MD_F.get_parent_class_lang(parent_class)
                    dl_code = lang_codes[detected_lang]
                    if detected_lang != new_lang:
                        changed = True
                        new_parent = MD_F.get_lang_parent_class(new_lang)
                        new_line = "%sclass %s(%s):%s" "" % (whitespace, name, new_parent, comments,)
                    else:
                        new_line = line
                    if new_line.endswith("  # noqa"):  # Remove flake8 skip
                        new_line = new_line[0 : -len("  # noqa")]
                    seleniumbase_lines.append(new_line)
                    added_line = True
                    continue
                elif parent_class in MD_F.get_masterqa_parent_classes_list():
                    detected_lang = MD_F.get_mqa_par_class_lang(parent_class)
                    dl_code = lang_codes[detected_lang]
                    if detected_lang != new_lang:
                        changed = True
                        new_parent = MD_F.get_mqa_lang_par_class(new_lang)
                        new_line = "%sclass %s(%s):%s" "" % (whitespace, name, new_parent, comments,)
                    else:
                        new_line = line
                    if new_line.endswith("  # noqa"):  # Remove flake8 skip
                        new_line = new_line[0 : -len("  # noqa")]
                    seleniumbase_lines.append(new_line)
                    added_line = True
                    continue
            if not added_line:
                # Probably a language missing from the translator.
                # Add the class definition line as it is and move on.
                seleniumbase_lines.append(line)
            continue

        if "self." in line and "(" in line and detected_lang and (detected_lang != new_lang):
            found_swap = False
            replace_count = line.count("self.")  # Total possible replacements
            for key in md.keys():
                original = "self." + md[key][dl_code] + "("
                if original in line:
                    replacement = "self." + md[key][nl_code] + "("
                    new_line = line.replace(original, replacement)
                    found_swap = True
                    replace_count -= 1
                    if replace_count == 0:
                        break  # Done making replacements
                    else:
                        # There might be another method to replace in the line.
                        # Example: self.assert_true("Name" in self.get_title())
                        line = new_line
                        continue

            if found_swap:
                if new_line.endswith("  # noqa"):  # Remove flake8 skip
                    new_line = new_line[0 : -len("  # noqa")]
                seleniumbase_lines.append(new_line)
                continue

        seleniumbase_lines.append(line)

    return seleniumbase_lines, changed, detected_lang


def main():
    colorama.init(autoreset=True)
    c1 = colorama.Fore.BLUE + colorama.Back.LIGHTCYAN_EX
    c2 = colorama.Fore.BLUE + colorama.Back.LIGHTYELLOW_EX
    c3 = colorama.Fore.RED + colorama.Back.LIGHTGREEN_EX
    c4 = colorama.Fore.BLUE + colorama.Back.LIGHTGREEN_EX
    c5 = colorama.Fore.RED + colorama.Back.LIGHTYELLOW_EX
    c6 = colorama.Fore.RED + colorama.Back.LIGHTCYAN_EX
    c7 = colorama.Fore.BLACK + colorama.Back.MAGENTA
    cr = colorama.Style.RESET_ALL
    expected_arg = "[A SeleniumBase Python file]"
    command_args = sys.argv[2:]

    seleniumbase_file = command_args[0]
    if not seleniumbase_file.endswith(".py"):
        raise Exception(
            "\n\n`%s` is not a Python file!\n\n" "Expecting: %s\n" % (seleniumbase_file, expected_arg)
        )

    new_lang = None
    overwrite = False
    copy = False
    print_only = False
    help_me = False
    if len(command_args) >= 2:
        options = command_args[1:]
        for option in options:
            option = option.lower()
            if option == "help" or option == "--help":
                help_me = True
            elif option == "-o" or option == "--overwrite":
                overwrite = True
            elif option == "-c" or option == "--copy":
                copy = True
            elif option == "-p" or option == "--print":
                print_only = True
            elif option == "--en" or option == "--english":
                new_lang = "English"
            elif option == "--zh" or option == "--chinese":
                new_lang = "Chinese"
            elif option == "--nl" or option == "--dutch":
                new_lang = "Dutch"
            elif option == "--fr" or option == "--french":
                new_lang = "French"
            elif option == "--it" or option == "--italian":
                new_lang = "Italian"
            elif option == "--ja" or option == "--japanese":
                new_lang = "Japanese"
            elif option == "--ko" or option == "--korean":
                new_lang = "Korean"
            elif option == "--pt" or option == "--portuguese":
                new_lang = "Portuguese"
            elif option == "--ru" or option == "--russian":
                new_lang = "Russian"
            elif option == "--es" or option == "--spanish":
                new_lang = "Spanish"
            else:
                invalid_cmd = "\n===> INVALID OPTION: >> %s <<" % option
                invalid_cmd = invalid_cmd.replace(">> ", ">>" + c5 + " ")
                invalid_cmd = invalid_cmd.replace(" <<", " " + cr + "<<")
                invalid_cmd = invalid_cmd.replace(">>", c7 + ">>" + cr)
                invalid_cmd = invalid_cmd.replace("<<", c7 + "<<" + cr)
                invalid_run_command(invalid_cmd)
    else:
        help_me = True

    specify_lang = (
        "\n>* You must specify a language to translate to! *<\n"
        "\n"
        ">    ********  Language Options:  ********    <\n"
        "   --en / --English    |    --zh / --Chinese\n"
        "   --nl / --Dutch      |    --fr / --French\n"
        "   --it / --Italian    |    --ja / --Japanese\n"
        "   --ko / --Korean     |    --pt / --Portuguese\n"
        "   --ru / --Russian    |    --es / --Spanish\n"
    )
    specify_action = (
        "\n>* You must specify an action type! *<\n"
        "\n"
        "> *** Action Options: *** <\n"
        "      -p / --print\n"
        "      -o / --overwrite\n"
        "      -c / --copy\n"
    )
    example_run = (
        "\n> *** Examples: *** <\n"
        "Translate test_1.py into Chinese and only print the output:\n"
        " >$ seleniumbase translate test_1.py --zh -p\n"
        "Translate test_2.py into Portuguese and overwrite the file:\n"
        " >$ seleniumbase translate test_2.py --pt -o\n"
        "Translate test_3.py into Dutch and make a copy of the file:\n"
        " >$ seleniumbase translate test_3.py --nl -c\n"
    )
    usage = "\n> *** Usage: *** <\n" " >$ seleniumbase translate [SB_FILE.py] [LANGUAGE] [ACTION]\n"
    specify_lang = specify_lang.replace(">*", c5 + ">*")
    specify_lang = specify_lang.replace("*<", "*<" + cr)
    specify_lang = specify_lang.replace("Language Options:", c4 + "Language Options:" + cr)
    specify_lang = specify_lang.replace(">    ********  ", c3 + ">    ********  " + cr)
    specify_lang = specify_lang.replace("  ********    <", c3 + "  ********    <" + cr)
    specify_lang = specify_lang.replace("--en", c2 + "--en" + cr)
    specify_lang = specify_lang.replace("--zh", c2 + "--zh" + cr)
    specify_lang = specify_lang.replace("--nl", c2 + "--nl" + cr)
    specify_lang = specify_lang.replace("--fr", c2 + "--fr" + cr)
    specify_lang = specify_lang.replace("--it", c2 + "--it" + cr)
    specify_lang = specify_lang.replace("--ja", c2 + "--ja" + cr)
    specify_lang = specify_lang.replace("--ko", c2 + "--ko" + cr)
    specify_lang = specify_lang.replace("--pt", c2 + "--pt" + cr)
    specify_lang = specify_lang.replace("--ru", c2 + "--ru" + cr)
    specify_lang = specify_lang.replace("--es", c2 + "--es" + cr)
    specify_lang = specify_lang.replace("--English", c2 + "--English" + cr)
    specify_lang = specify_lang.replace("--Chinese", c2 + "--Chinese" + cr)
    specify_lang = specify_lang.replace("--Dutch", c2 + "--Dutch" + cr)
    specify_lang = specify_lang.replace("--French", c2 + "--French" + cr)
    specify_lang = specify_lang.replace("--Italian", c2 + "--Italian" + cr)
    specify_lang = specify_lang.replace("--Japanese", c2 + "--Japanese" + cr)
    specify_lang = specify_lang.replace("--Korean", c2 + "--Korean" + cr)
    specify_lang = specify_lang.replace("--Portuguese", c2 + "--Portuguese" + cr)
    specify_lang = specify_lang.replace("--Russian", c2 + "--Russian" + cr)
    specify_lang = specify_lang.replace("--Spanish", c2 + "--Spanish" + cr)
    specify_action = specify_action.replace(">*", c6 + ">*")
    specify_action = specify_action.replace("*<", "*<" + cr)
    specify_action = specify_action.replace("Action Options:", c4 + "Action Options:" + cr)
    specify_action = specify_action.replace("> *** ", c3 + "> *** " + cr)
    specify_action = specify_action.replace(" *** <", c3 + " *** <" + cr)
    specify_action = specify_action.replace(" -p", " " + c1 + "-p" + cr)
    specify_action = specify_action.replace(" -o", " " + c1 + "-o" + cr)
    specify_action = specify_action.replace(" -c", " " + c1 + "-c" + cr)
    specify_action = specify_action.replace(" --print", " " + c1 + "--print" + cr)
    specify_action = specify_action.replace(" --overwrite", " " + c1 + "--overwrite" + cr)
    specify_action = specify_action.replace(" --copy", " " + c1 + "--copy" + cr)
    example_run = example_run.replace("Examples:", c4 + "Examples:" + cr)
    example_run = example_run.replace("> *** ", c3 + "> *** " + cr)
    example_run = example_run.replace(" *** <", c3 + " *** <" + cr)
    example_run = example_run.replace(" -p", " " + c1 + "-p" + cr)
    example_run = example_run.replace(" -o", " " + c1 + "-o" + cr)
    example_run = example_run.replace(" -c", " " + c1 + "-c" + cr)
    example_run = example_run.replace("Chinese", c2 + "Chinese" + cr)
    example_run = example_run.replace("Portuguese", c2 + "Portuguese" + cr)
    example_run = example_run.replace("Dutch", c2 + "Dutch" + cr)
    example_run = example_run.replace(" --zh", " " + c2 + "--zh" + cr)
    example_run = example_run.replace(" --pt", " " + c2 + "--pt" + cr)
    example_run = example_run.replace(" --nl", " " + c2 + "--nl" + cr)
    usage = usage.replace("Usage:", c4 + "Usage:" + cr)
    usage = usage.replace("> *** ", c3 + "> *** " + cr)
    usage = usage.replace(" *** <", c3 + " *** <" + cr)
    usage = usage.replace("SB_FILE.py", c4 + "SB_FILE.py" + cr)
    usage = usage.replace("LANGUAGE", c2 + "LANGUAGE" + cr)
    usage = usage.replace("ACTION", c1 + "ACTION" + cr)

    if help_me:
        message = specify_lang + specify_action + example_run + usage
        raise Exception(message)
    if not overwrite and not copy and not print_only:
        message = specify_action + example_run + usage
        if not new_lang:
            message = specify_lang + specify_action + example_run + usage
        raise Exception(message)
    if not new_lang:
        raise Exception(specify_lang + example_run + usage)
    if overwrite and copy:
        part_1 = "\n* You can choose either {-o / --overwrite} " "OR {-c / --copy}, but NOT BOTH!\n"
        part_1 = part_1.replace("-o ", c1 + "-o" + cr + " ")
        part_1 = part_1.replace("--overwrite", c1 + "--overwrite" + cr)
        part_1 = part_1.replace("-c ", c1 + "-c" + cr + " ")
        part_1 = part_1.replace("--copy", c1 + "--copy" + cr)
        message = part_1 + example_run + usage
        raise Exception(message)

    with open(seleniumbase_file, "r", encoding="utf-8") as f:
        all_code = f.read()
    if "def test_" not in all_code and "from seleniumbase" not in all_code:
        raise Exception(
            "\n\n`%s` is not a valid SeleniumBase test file!\n"
            "\nExpecting: %s\n" % (seleniumbase_file, expected_arg)
        )
    code_lines = all_code.split("\n")

    seleniumbase_lines, changed, d_l = process_test_file(code_lines, new_lang)
    detected_lang = d_l

    if not changed:
        msg = "\n*> [%s] was already in %s! * No changes were made! <*\n" "" % (seleniumbase_file, new_lang,)
        msg = msg.replace("*> ", "*> " + c2).replace(" <*", cr + " <*")
        print(msg)
        return

    save_line = (
        "[[[[%s]]]] was translated to [[[%s]]]! "
        "(Previous: %s)\n"
        "" % (seleniumbase_file, new_lang, detected_lang)
    )
    save_line = save_line.replace("[[[[", "" + c4)
    save_line = save_line.replace("]]]]", cr + "")
    save_line = save_line.replace("[[[", "" + c2)
    save_line = save_line.replace("]]]", cr + "")

    if print_only:
        print("")
        print(save_line)
        print(c1 + "* Here are the results: >>>" + cr)
        print("--------------------------------------------------------------")
        for line in seleniumbase_lines:
            print(line)
        print("--------------------------------------------------------------")

    new_file_name = None
    if copy:
        base_file_name = seleniumbase_file.split(".py")[0]
        new_locale = MD_F.get_locale_code(new_lang)
        new_ext = "_" + new_locale + ".py"
        for locale in MD_F.get_locale_list():
            ext = "_" + locale + ".py"
            if seleniumbase_file.endswith(ext):
                base_file_name = seleniumbase_file.split(ext)[0]
                break
        new_file_name = base_file_name + new_ext
    elif overwrite:
        new_file_name = seleniumbase_file
    else:
        pass  # Print-only run already done

    if not print_only:
        print("")
        print(save_line)
    else:
        pass  # Print-only run already done

    if new_file_name:
        out_file = codecs.open(new_file_name, "w+", encoding="utf-8")
        out_file.writelines("\r\n".join(seleniumbase_lines))
        out_file.close()
        results_saved = "The translation was saved to: [[[%s]]]\n" "" % new_file_name
        results_saved = results_saved.replace("[[[", "" + c1)
        results_saved = results_saved.replace("]]]", cr + "")
        print(results_saved)


if __name__ == "__main__":
    invalid_run_command()
