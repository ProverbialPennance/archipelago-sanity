import re

Items = [
    'RatCloak', 'WaveBangle', 'RatBurst', 'Feather', 'PurpleLocket', 'SanguineFin', 'BloodGem', 'RatDasher', 'IceGem',
    'DreamersCrown', 'StormsGem', 'Wallkicks', 'DeathGem', 'MagicBroom', 'Heart', 'LuckyFrog', 'MagicSoap',
    'BigLeagueGlove'
]

MultiItems = [
    'MagicBolt', 'Baseball', 'Sparksuit',
]


def get_parens(file, count=0):
    ret = ""
    while count > 0 or not ret:
        line = file.readline()
        ret += line
        count += line.count("(") - line.count(")")
    return ret.strip()


def lambda_to_lua(text):
    text = text.replace('\n', ' ').replace('\r', '')
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\((\w+) in loadout\)", r"\1()", text)
    text = re.sub(r"(\w+) in loadout", r"\1()", text)
    text = re.sub(r"\(loadout.count\((\w+)\) >= (\d+)\)", r"\1(\2)", text)
    text = text.replace("True", "true").replace("False", "false")
    return text


with open('logic_rules.lua', 'w') as out_file:
    for item in MultiItems:
        out_file.write(
            f'{item} = function(count) return Tracker:ProviderCountForCode("{item}") / 5  >= (count or 1) end\n')
    for item in Items:
        out_file.write(
            f'{item} = function(count) return Tracker:ProviderCountForCode("{item}") >= (count or 1) end\n')
    out_file.write('\n')

    with open('defaultLogic.py', 'r') as source_file:
        line = True
        while line:
            line = source_file.readline()
            ret = re.search(r"(\w+) = LogicShortcut\(lambda loadout: \(", line)
            if ret is not None:
                lambda_code = get_parens(source_file, 2)
                lambda_code = lambda_to_lua(lambda_code)
                out_file.write(f'{ret.group(1)} = function() return {lambda_code[:-2]} end\n')
    out_file.write('\n')

    out_file.write('LOCATIONS = {')
    with open('defaultLogic.py', 'r') as source_file:
        line = True
        while line:
            line = source_file.readline()
            ret = re.search(r"\"(.+)\": lambda loadout: \(", line)
            if ret is not None:
                lambda_code = get_parens(source_file, 1)
                lambda_code = lambda_to_lua(lambda_code)
                out_file.write(f'["{ret.group(1)}"] = function() return {lambda_code[:-2]} end,\n')
    out_file.write('}\n')
