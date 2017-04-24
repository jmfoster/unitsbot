units = ["inches", "in", "inch", "pounds", "pound", "lb", "lbs", "centimeters", "cm", "kilograms", "kg", "kgs"]
msg = "Man, I think I was over 115lb in 4th grade."

in2cm = 2.54
cm2in = 0.393701
lb2kg = 0.453592
kg2lb = 2.20462
ft2cm = 30.48

#conversions = {"inches":in2cm, "in":in2cm, "inch":in2cm, "pounds":lb2kg, "pound":lb2kg, "lb":lb2kg, "lbs":lb2kg, "centimeters":cm2in, "cm":cm2in, "kilograms":kg2lb, "kg":kg2lb, "kgs":kg2lb}
distances = {"inches":in2cm, "in":in2cm, "inch":in2cm, "feet":ft2cm, "foot":ft2cm, "ft":ft2cm, "centimeters":cm2in, "cm":cm2in}
weights = {"pounds":lb2kg, "pound":lb2kg, "lb":lb2kg, "lbs":lb2kg, "kilograms":kg2lb, "kg":kg2lb, "kgs":kg2lb}

unit_swap = {"inches":"cm", "in":"cm", "inch":"cm", "feet":"cm", "foot":"cm", "ft":"cm", "pounds":"kg", "pound":"kg", "lb":"kg", "lbs":"kg", "centimeters":"in", "cm":"in", "kilograms":"lbs", "kg":"lbs", "kgs":"lbs"}

import re

def convert_units(msg):
    responses = []
    matches = re.findall(r"([0-9]+\')+\s*([0-9]+\")?\s*", msg)
    for match in matches:
        feet, inches = match
        feet = feet.strip("'")
        inches = inches.strip('"')
        if feet:
            feet = float(feet)
        else:
            feet = 0
        if inches:
            inches = float(inches)
        else:
            inches = 0
        if feet or inches:
            total_inches = feet*12 + inches
            converted_number = total_inches * distances["inches"]
            response = " ".join(match), "=", format(converted_number, '.2f'), "cm"
            responses.append(" ".join(response))
    for unit in distances:
        matches = re.findall(r"([0-9]+\.?[0-9]*)\s*"+"("+unit+")", msg)
        for match in matches:
            number, unit = match
            converted_number = float(number) * distances[unit]
            response = number, unit, "=", format(converted_number, '.2f'), unit_swap[unit]
            responses.append(" ".join(response))
        if matches:
            break
    for unit in weights:
        matches = re.findall(r"([0-9]+\.?[0-9]*)\s*"+"("+unit+")", msg)
        for match in matches:
            number, unit = match
            converted_number = float(number) * weights[unit]
            response = number, unit, "=", format(converted_number, '.2f'), unit_swap[unit]
            responses.append(" ".join(response))
        if matches:
            break
    return "\n".join(responses)
