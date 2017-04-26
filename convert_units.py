# -*- coding: utf-8 -*-
import re
from pint import UnitRegistry
from pint import UndefinedUnitError, DimensionalityError

units = ["inches", "in", "inch", "pounds", "pound", "lb", "lbs", "centimeters", "cm", "kilograms", "kg", "kgs"]

in2cm = 2.54
cm2in = 0.393701
lb2kg = 0.453592
kg2lb = 2.20462
ft2cm = 30.48
oz2g = 28.3495
g2oz = 0.035274

#conversions = {"inches":in2cm, "in":in2cm, "inch":in2cm, "pounds":lb2kg, "pound":lb2kg, "lb":lb2kg, "lbs":lb2kg, "centimeters":cm2in, "cm":cm2in, "kilograms":kg2lb, "kg":kg2lb, "kgs":kg2lb}
distances = {"inches":in2cm, "in":in2cm, "inch":in2cm, "feet":ft2cm, "foot":ft2cm, "ft":ft2cm, "centimeters":cm2in, "cm":cm2in}
weights = {"grams":g2oz, "gram":g2oz, "ounces":oz2g, "ounce":oz2g, "oz":oz2g, "pounds":lb2kg, "pound":lb2kg, "lb":lb2kg, "lbs":lb2kg, "kilograms":kg2lb, "kg":kg2lb, "kgs":kg2lb}

unit_swap = {"grams":"ounces", "gram":"ounce", "ounces":"grams", "ounce":"gram", "oz":"g", "inches":"cm", "in":"cm", "inch":"cm", "feet":"cm", "foot":"cm", "ft":"cm", "pounds":"kg", "pound":"kg", "lb":"kg", "lbs":"kg", "centimeters":"in", "cm":"in", "kilograms":"lbs", "kg":"lbs", "kgs":"lbs"}

# pint
ureg = UnitRegistry()
Q_ = ureg.Quantity

#msg = '1 foot in inches'



def pint_convert(msg):
    response = ''
    if ' to ' in msg:
        try:
            src, dst = msg.split(' to ')
            converted_quantity = Q_(src).to(dst)
            response = u'{0} = {1}'.format(src, converted_quantity)
        except UndefinedUnitError as e:
            response = "Doh! I didn't recognize all those units."
        except DimensionalityError as e:
            response = "Doh! I " + str(e).lower()
        except:
            #response = "ಠ_ಠ"
            response = 'Usage example: "@unitsbot 1 kg to pounds"'
    else:
        response = 'Usage example: "@unitsbot 1 kg to pounds"'
    #print "pint_convert response", response
    return response

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
            response = " ".join(match), u"\u2248", format(converted_number, '.0f'), "cm"
            responses.append(" ".join(response))
    for unit in distances:
        matches = re.findall(r"([0-9]+\.?[0-9]*)\s*"+"("+unit+")", msg)
        for match in matches:
            number, unit = match
            converted_number = float(number) * distances[unit]
            response = number, unit, u"\u2248", format(converted_number, '.0f'), unit_swap[unit]
            responses.append(" ".join(response))
        if matches:
            break
    for unit in weights:
        matches = re.findall(r"([0-9]+\.?[0-9]*)\s*"+"("+unit+")", msg)
        for match in matches:
            number, unit = match
            converted_number = float(number) * weights[unit]
            response = number, unit, u"\u2248", format(converted_number, '.0f'), unit_swap[unit]
            responses.append(" ".join(response))
        if matches:
            break
    return "\n".join(responses)


if __name__ == "__main__":
    pint_convert("1 foot in inches")
    pint_convert("12 inches to cm")
