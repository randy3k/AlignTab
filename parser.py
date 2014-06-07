import re

def input_parser(user_input):
    m = re.match(r"(.+)/([lcr*()0-9]*)(f[0-9]*)?", user_input)

    if m and (m.group(2) or m.group(3)):
        regex = m.group(1)
        option = m.group(2)
        f = m.group(3)
    else:
        # print("No options!")
        return [user_input, [['l', 1]], 0]

    try:
        # for option
        rParan = re.compile(r"\(([^())]*)\)\*([0-9]+)")
        while True:
            if not rParan.search(option): break
            for r in rParan.finditer(option):
                option = option.replace(r.group(0), r.group(1)*int(r.group(2)),1)

        for r in re.finditer(r"([lcr][0-9]*)\*([0-9]+)", option):
            option = option.replace(r.group(0), r.group(1)*int(r.group(2)),1)

        option = re.findall(r"[lcr][0-9]*", option)
        option = list(map(lambda x: [x[0], 1] if len(x)==1 \
                                    else [x[0], int(x[1:])], option))
        option = option if option else [['l', 1]]

        # for f
        f = 0 if not f else 1 if len(f)==1 else int(f[1:])
    except:
        [regex, option ,f]= [user_input, [['l', 1]], 0]

    return [regex, option ,f]